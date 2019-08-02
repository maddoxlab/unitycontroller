# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 07:29:16 2019

@author: mcappelloni
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 09:27:18 2019

@author: maddy
"""
import numpy as np
from _unitycontroller import UnityShape
from expyfun.stimuli import window_edges
from expyfun.io import write_hdf5
import argparse
from pythonosc import udp_client, dispatcher, osc_server
import matplotlib.pyplot as plt
import scipy.signal as sig
#import soundfile as sf
from scipy.io import wavfile
import os
import json

#from pathlib import Path
 
# %% SETUP
# Experiment parameters

# General
n_trials = 12
n_max_obj = 3
dur = 15
mod_fmin = 0.1
mod_fmax = 5
stim_folder = "C:\\Users\\mcappelloni\\Sandbox2\\Assets\\Resources\\"
cue_dur = 1.

blip_t_min = 1
blip_t_max = dur - 1
blip_n_min = 1
blip_n_max = 2
blip_size = 1.5 # in semitones
blip_dur = 100e-3  # length of aud perturbation in s
env_offset = 2.5
vis_scale = 4
blip_thresh = env_offset # offset = loudest 50% across target and distractors
IBI_min = 1 # minimum inter-blip-interval

# Auditory stimuli
fs = 48000
f0 = [323, 391, 440]
n_harmonics = 8
rms = 0.01


# Visual stimuli
radius = 1
r_dist = 1.5
fps = 90
tr_f_min = .02
tr_f_max = 1
bounds_az = [-np.pi / 2, np.pi / 2]
bounds_el = [-np.pi / 2, np.pi / 2]
bounds = [bounds_az, bounds_el]
base_colors = 3 * [1]
blip_colors = 3 * [.5]
blip_len = 15

def extremify(x, deg=1):
    y = np.copy(x)
    for _ in range(deg):
        y = -np.cos(y * np.pi) / 2 + 0.5
    return y

### FUNCTION FOR MAKING ENVELOPES ###
def generate_noise(dur, fs, min_freq, max_freq, rms, spect_env='white', do_extremify=True, extremify_deg=2):
   '''Generate noise in a given frequency band with a given spectral envelope
   Inputs
   ------
   dur: float
       Duration in seconds
   fs: int
       Sampling frequency
   min_freq: int or float
       Minimum frequency included in the noise band
   max_freq: int or float
       Maximum frequency included in the noise band
   rms: float
       Desired rms amplitude
   spect_env: string
       'white' for flat envelope, 'pink' for 1/f enveleope'''
   noise_len = int(dur * fs)
   storage = np.zeros(noise_len, dtype=np.complex)
   f_noise = np.arange(0, noise_len) * float(fs) / noise_len
   f_ind = (f_noise < max_freq) & (f_noise > min_freq)
   if spect_env == 'white':
       storage[f_ind] = 1.
   elif spect_env == 'pink':
       storage[f_ind] = 1. / f_noise[f_ind]
   storage[f_ind] = np.exp(1j * 2 * np.pi * np.random.rand(np.sum(f_ind)))
   storage[-1:noise_len // 2:-1] = np.conj(storage[1:(noise_len + 1) // 2:1])
   noise = np.real(np.fft.ifft(storage))
   
   noise -= np.min(noise)
   noise /= np.max(noise)
   if do_extremify:
       noise = extremify(noise, extremify_deg)
   noise *= rms / np.std(noise)
   return noise - np.mean(noise)


### FUNCTION FOR MAKING HARMONIC STIMULI ###
def generate_harmonic_tone(dur, fs, f0, n_harmonics, rms):
    time = np.arange(fs * dur) / fs
    harmonics = np.zeros((n_harmonics, len(time)))
    if np.array(f0).shape:
        for i in np.arange(n_harmonics):
            harmonics[i] = np.cos(np.cumsum(2 * np.pi * (f0 * (i + 1)) * 1 / fs))
    else:
        for i in np.arange(n_harmonics):
            harmonics[i] = np.cos(2 * np.pi * (f0 * (i + 1)) * time)
    harmonics = np.sum(harmonics, 0)
    harmonics *= rms / np.std(harmonics)
    return harmonics - harmonics.mean()

# Make auditory cues
for f in f0:
    a_cue = generate_harmonic_tone(cue_dur, fs, f, n_harmonics, rms)
    cue_path = os.path.join(stim_folder, 'cue_{}.wav'.format(int(f)))
    wavfile.write(cue_path, fs, a_cue)

# Make stimulus envelopes 
aud_env = -1 * np.ones((n_trials, n_max_obj, int(dur*fs)))
vis_env_coh = np.zeros((n_trials, n_max_obj, int(dur*fps)))
vis_env_incoh = -1 * np.ones((n_trials, n_max_obj, int(dur*fps)))
trajectories = np.zeros((n_trials, n_max_obj * 2, 3, int(dur*fps)))
aud_stim = np.zeros((n_trials, n_max_obj, int(dur * fs)))
vis_stim = np.ones((n_trials, n_max_obj, int(dur * fps))) 
rotation = np.zeros((n_trials, n_max_obj, 2, int(dur * fps)))

time = np.arange(int(dur * fs)) / fs
blip_len_aud = int(blip_dur * fs)
trl = 0
while trl < n_trials:
#    plt.figure()
    for obj in np.arange(n_max_obj):
        while any(aud_env[trl, obj] < 0):
            aud_env[trl, obj] = generate_noise(dur, fs, mod_fmin, mod_fmax, 1,
                                 'white') + env_offset   
            print([trl, obj])
        vis_env_coh[trl, obj] = sig.resample(aud_env[trl, obj], 
                                             int(fps * dur)) / vis_scale # same envelope if coherent
        while any(vis_env_incoh[trl, obj] < 0):
            vis_env_incoh[trl, obj] = sig.resample((generate_noise(dur, fs, 
                                                                  mod_fmin,
                                                                  mod_fmax, 1, 
                                                                  'white')
                                                                  + env_offset),
                                                    int(fps * dur)) / vis_scale

    # Spatial trajectories (in spherical coordinates)
    temp_traj = np.zeros((n_max_obj * 2, 2, int(dur*fps)))
    for traj in np.arange(n_max_obj * 2):
        for dim in np.arange(2):
            temp_traj[traj, dim] = generate_noise(dur, fps, tr_f_min, 
                                                 tr_f_max, 1, do_extremify=False,
                                                 extremify_deg=1)
        
            temp_traj[:, dim] *= (np.diff(bounds[dim]) / 
                                    (temp_traj[:, dim].max() - 
                                     temp_traj[:, dim].min()))
            temp_traj[:, dim] += np.mean(bounds[dim])
    temp_traj[:, 1] *= -1
    temp_traj[:, 1] += np.pi / 2
    
    rotation[trl, :, 0] = temp_traj[:n_max_obj, 0]
    rotation[trl, :, 1] = temp_traj[:n_max_obj, 1]
    
    # Convert spherical to cartesian coordinates
    trajectories[trl, :, 2] = (r_dist * np.cos(temp_traj[:, 0]) *
                               np.sin(temp_traj[:, 1]))
    trajectories[trl, :, 0] = (r_dist * np.sin(temp_traj[:, 0]) *
                               np.sin(temp_traj[:, 1]))
    trajectories[trl, :, 1] = r_dist * np.cos(temp_traj[:, 1])
#    for i in np.arange(2 * n_max_obj):
#        plt.subplot(3, 2, i + 1)
#        for ii in np.arange(3):
#            plt.plot(trajectories[trl, i, ii, :])
#    plt.tight_layout()

    # BLip logic
    legal_blips = np.ones((int(dur*fs),), dtype='bool')
    legal_blips[time < blip_t_min] = 0
    legal_blips[time > blip_t_max] = 0
    
    legal_blips[[any(aud_env[trl, :, i] < blip_thresh) 
                 for i in np.arange(int(dur * fs))]] = 0
#    plt.plot(time, legal_blips, 'k')
    
    # Treat each legal interval as a potential event
    event_starts = np.where(np.diff(np.array(legal_blips, dtype=int)) > 0)[0]
    event_ends = np.where(np.diff(np.array(legal_blips, dtype=int)) < 0)[0]
#    plt.plot(time[event_starts], event_starts > 0, 'go')
#    plt.plot(time[event_ends], event_ends > 0, 'rs')
    events = []
    for start, end in zip(event_starts, event_ends):
        raw_blip_time = start + np.random.choice(end - start)
        frame_blip_time = round(raw_blip_time / fs * fps) / fps * fs
        events.append(frame_blip_time)
#    plt.plot(time[events], np.array(events) > 0, 'cd')
    
    # Randomize order of event and only include ones that pass IBI
    ordered_events = np.random.permutation(events)
    blips = [ordered_events[0]]
    for o in ordered_events:
        if all(np.abs(o - np.array(blips)) > IBI_min * fs):
            blips.append(o)
    blips = np.array(blips)
#    plt.plot(time[np.array(blips)], np.array(blips) > 0, 'y*', ms=20)
    
    # See if the number of blips can satisfy max & min constraints
    if (len(blips) < (blip_n_min * n_max_obj * 2) or 
        len(blips) > (blip_n_max * n_max_obj * 2)):
        print('Bad trial')
    else:
        which_blips = np.random.randint(0, n_max_obj * 2, (len(blips),))
        # Make sure that 1) all streams are represented
        # 2) max blips not violated for any streams
        # 3) min blips not violated for any stream
        # if any are false, regenerate the blips
        while (len(np.unique(which_blips)) < (n_max_obj * 2) or 
               any(np.unique(which_blips, return_counts=True)[1] > blip_n_max) or
               any(np.unique(which_blips, return_counts=True)[1] < blip_n_min)):
            which_blips = np.random.randint(0, n_max_obj * 2, (len(blips),))
            
        # plot final blip
#        [plt.plot([0, dur], [i, i], 'k-') for i in np.arange(n_max_obj * 2)]
#        [plt.plot(time[blips[which_blips==i]], i * (blips[which_blips==i] > 0), 'ro') for i in np.arange(n_max_obj * 2)]
#        print(which_blips)
        
        # make orth feature stim
        blip_env_aud = blip_size * np.sin(2 * np.pi / blip_dur * time[0:blip_len_aud])
        f_env = np.zeros((n_max_obj, int(dur * fs)))
        
        for i, c in enumerate(base_colors):
            vis_stim[trl, i] *= c
        for w, b in zip(which_blips, blips):
            if w < n_max_obj: # auditory blip assignment
                f_env[w, int(b):(int(b) + blip_len_aud)] = blip_env_aud
            else:
                blip_ind = int(b * fps / fs)
                vis_stim[trl, w - n_max_obj, blip_ind:(blip_ind + blip_len)] = blip_colors[w - n_max_obj]
    
        for i, f_carr in enumerate(f0):
            aud_stim[trl, i] = generate_harmonic_tone(dur, fs, f_carr * 2 ** (f_env[i] / 12), n_harmonics, rms)
        aud_stim *= aud_env
        
        
        # SAVE EVERYTHING
        for s in np.arange(n_max_obj):
            aud_path = os.path.join(stim_folder, 'A_trl_{}_obj_{}.wav'.format(int(trl), int(s)))
            wavfile.write(aud_path, fs, aud_stim[trl, s])
    
        # update trial count
        trl += 1
rotation = 180 * rotation / np.pi

#write_hdf5('stimulus_data.hdf5',
#           dict(vis_stim=vis_stim, aud_env=aud_env, vis_env_coh=vis_env_coh,
#                vis_env_incoh=vis_env_incoh, trajectories=trajectories,
#                rotation=rotation),
#           overwrite=True)

stimdata = dict(vis_stim=vis_stim.tolist(), vis_env_coh=vis_env_coh.tolist(),
                vis_env_incoh=vis_env_incoh.tolist(), 
                trajectories=trajectories.tolist(), rotation=rotation.tolist())
#stimdata = list(stimdata)
with open('stim_data.json', 'w') as outfile:
    json.dump(stimdata, outfile)
           
#    while any(np.diff(time[legal_blips]) < IBI_min):
#        violations = np.diff(time[legal_blips]) < IBI_min
#        which = np.random.choice(len(violations))
#        ind = np.where(legal_blips)[0][which]
#        legal_blips[ind + int(np.random.rand() > 0.5)] = 0

#    
#    
#    # figure out which condition
#    spat_idx = trl % len(spat_cong)
#    temp_idx = (trl // len(spat_cong)) % len(temp_coh)
#    n_obj_idx = ((trl // len(spat_cong)) // len(temp_coh)) % len(n_objects)
#    
#    # choose n_object condition
#    n_object = n_objects[n_obj_idx]
#    
#    # randomly set f0's
#    f0_trl = np.array(np.random.choice(f0, (n_object,), replace=False))
#    
#    
#    # pick which one will be the target
#    target = np.random.randint(0, n_object)
#    
#    # make auditory cue
#    a_cue = generate_harmonic_tone(cue_dur, fs, f0_trl[target], 
#                                   n_harmonics, rms)
#    a_cue_pre = window_edges(a_cue, fs, 0.02)
#    a_cue = np.concatenate((np.zeros((int(av_delay * fs), )), a_cue_pre), 0)
#    
#    vis_envelopes = []
#    aud_envelopes = []
#    
#    # make envelopes and auditory stim
#    aud_active = []
#    for i, f in zip(np.arange(n_object), f0_trl):
#        a_env = generate_noise(dur, fs, mod_fmin, mod_fmax, 1,
#                             'white') + env_offset
#        aud_envelopes.append(a_env)
#        noise = generate_harmonic_tone(dur, fs, f, n_harmonics, rms)
#        noise_mod = a_env * noise
#        noise_mod *= rms / np.std(noise_mod)
#        noise_mod = window_edges(noise_mod, fs)
#        if temp_coh[temp_idx]:
#            env_ds = sig.resample(a_env, int(fps * dur)) / 4
#        else: # make other vis env
#            v_env = generate_noise(dur, fs, mod_fmin, mod_fmax, 1,
#                                   'white') + env_offset
#            env_ds = sig.resample(v_env, int(fps * dur)) / 4
#            
#        vis_envelopes.append(env_ds)
#        
#        if spat_cong[spat_idx]: # figure out where to put the sound
#            sound_id = i
#            n_trajectory = n_object
#        else:
#            sound_id = i + n_objects[-1]
#            n_trajectory = 2 * n_object
#        aud_path = os.path.join(stim_folder,
#                                'marble_planet_sound{}.wav'.format(int(sound_id)))
#        print('marble_planet_sound{}.wav'.format(int(sound_id)))
#        aud_active.append(sound_id)
#        if i == target:
#            wavfile.write(aud_path, fs, np.concatenate((a_cue, noise_mod),
#                                                       0))
#            #sf.write(aud_path, np.concatenate((a_cue, noise_mod),0), fs)
#        else:
#            wavfile.write(aud_path, fs, 
#                          np.concatenate((np.zeros(a_cue.shape), 
#                                          noise_mod), 0))
#    
#    
#    vis_envelopes = np.array(vis_envelopes)
#    aud_envelopes = np.array(aud_envelopes)      
#    # make trajectories
#    trajectories = np.zeros((n_trajectory, 3, len(env_ds)))
#    for ii in np.arange(3):
#        for i in np.arange(n_trajectory):
#            trajectories[i, ii] = generate_noise(dur, fps, tr_f_min, 
#                                                 tr_f_max, 0.01)
#        
#        trajectories[:, ii] *= (np.diff(bounds[ii]) / 
#                                (trajectories[:, ii].max() - 
#                                 trajectories[:, ii].min()))
#        trajectories[:, ii] += np.mean(bounds[ii])
#    write_hdf5('stim_info_trl{}'.format(int(trl)) + ec.participant + '.hdf5',
#               dict(vis=vis_envelopes, aud=aud_envelopes, tra=trajectories), overwrite=True)
#    # vis ready for cue
#    [shape.set_sca(3 * [.1 * e + .1]) for shape, e in zip(shapes, vis_envelopes[:, 0])]
#    shapes[target].set_visible(True)
#    shapes[target].set_pos(trajectories[target, :, 0])
#    shapes[target + 6].set_pos(trajectories[target, :, 0])
#    
#    for i in aud_active:
#        client.send_message('/fname{}'.format(int(i)),
#                            'marble_planet_sound{}.wav'.format(int(i)))
#        server.handle_request()
#    client.send_message('/start_query', [0])
#    server.handle_request()
#    client.send_message('/Play', [0])
#    
#    start = ec.current_time
#    ec.wait_until(start + av_delay)
#    shapes[target].draw()
#    shapes[target].send()
#    shapes[target + 6].draw()
#    shapes[target + 6].send()
##        [s.set_visible(True) for s in shapes[:n_object]]
#    for i, (vis_env, traj) in enumerate(zip(vis_envelopes.T, 
#                                         trajectories.transpose(2, 0, 1))):
#        
#        [shape.set_sca(3 * [.1 * e + .1]) for e, shape in zip(vis_env, 
#                                                              shapes[:n_object])]
#        [shape.set_pos(tr) for tr, shape in zip(traj, shapes[:6])]
#        [shape.set_pos(tr) for tr, shape in zip(traj[:3], shapes[6:])]
#        [shape.draw() for shape in shapes]
#        ec.wait_until(start + av_delay + cue_dur + (i + 1) / fps)
#        [shape.send() for shape in shapes]
#    ec.wait_secs(1)
#    client.send_message('/Clear_audio', [0])
#    #for i in aud_active:
#    #    try:
#    #        os.remove(stim_folder + 'marble_planet_sound{}.ogg'.format(int(i)))
#    #    except:
#    #        print('no file')
