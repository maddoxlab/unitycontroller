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
from expyfun import ExperimentController
from expyfun.stimuli import window_edges
from expyfun.io import write_hdf5
import argparse
from pythonosc import udp_client, dispatcher, osc_server
import matplotlib.pyplot as plt
import scipy.signal as sig
import soundfile as sf
import os as os
#from pathlib import Path
 
# %% SETUP
# Experiment parameters

# General
n_trl = 12
n_objects = [3]
spat_cong = [0]
temp_coh = [0, 1]
#n_objects = [3]
#spat_cong = [1]
#temp_coh = [1]
dur = 9.15
mod_fmin = 0.1
mod_fmax = 5
stim_folder = "C:\\Users\\mcappelloni\\Sandbox2\\Assets\\Resources\\"
cue_dur = 1.
av_delay = .1

# Auditory stimuli
fs = 48000
f0 = [323, 391, 440]
n_harmonics = 8
rms = 0.01
env_offset = 2
#f_max = np.logspace(11, 12, 5, base=2)

# Visual stimuli
radius = 1
fps = 90
tr_f_min = 0.01
tr_f_max = 0.2
z_bound = [3, 4]
x_bound = [-3, 3]
y_bound = [-1, 1]
bounds = [x_bound, y_bound, z_bound]

### FUNCTION FOR MAKING ENVELOPES ###
def generate_noise(dur, fs, min_freq, max_freq, rms, spect_env='white'):
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
   noise *= rms / np.std(noise)
   return noise - noise.mean()


### FUNCTION FOR MAKING HARMONIC STIMULI ###
def generate_harmonic_tone(dur, fs, f0, n_harmonics, rms):
    time = np.arange(fs * dur) / fs
    harmonics = np.zeros((n_harmonics, len(time)))
    for i in np.arange(n_harmonics):
        harmonics[i] = np.cos(2 * np.pi * (f0 * (i + 1)) * time)
    harmonics = np.sum(harmonics, 0)
    harmonics *= rms / np.std(harmonics)
    return harmonics - harmonics.mean()
        

# %% Set up OSC
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5005)
args_client = parser.parse_args()

client = udp_client.SimpleUDPClient(args_client.ip, args_client.port)

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1")
parser.add_argument("--port", type=int, default=6161)
args_serve = parser.parse_args()

def start_trial(address, *args):
    pass
def loaded(address, *args):
    pass
    
dispatcher = dispatcher.Dispatcher()
dispatcher.map('/start_ok', start_trial)
dispatcher.map('/loaded', loaded)

server = osc_server.BlockingOSCUDPServer((args_serve.ip, args_serve.port), 
                                         dispatcher)
server.timeout = 3

# %% Set trial order
trl_ID = np.random.permutation(np.arange(n_trl))

# %% EC
with ExperimentController('test_unity', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          full_screen=False) as ec:
    
    shapes = [UnityShape(ec, client,
                         int(i)) for i in np.arange(n_objects[-1] * 3)]
    ec.wait_secs(5)
    for trl in trl_ID:
        [s.set_sca([0, 0, 0]) for s in shapes]
        [s.set_sca([.2, .2, .2]) for s in shapes[6:]]
        [s.set_color([.5, .5, .5, 1]) for s in shapes[6:]]
        [s.set_rot([180, 0, 0]) for s in shapes[6:]]

        [s.draw() for s in shapes]
        [s.send() for s in shapes]
        # figure out which condition
        spat_idx = trl % len(spat_cong)
        temp_idx = (trl // len(spat_cong)) % len(temp_coh)
        n_obj_idx = ((trl // len(spat_cong)) // len(temp_coh)) % len(n_objects)
        
        # choose n_object condition
        n_object = n_objects[n_obj_idx]
        
        # randomly set f0's
        f0_trl = np.array(np.random.choice(f0, (n_object,), replace=False))
        
        
        # pick which one will be the target
        target = np.random.randint(0, n_object)
        
        # make auditory cue
        a_cue = generate_harmonic_tone(cue_dur, fs, f0_trl[target], 
                                       n_harmonics, rms)
        a_cue_pre = window_edges(a_cue, fs, 0.02)
        a_cue = np.concatenate((np.zeros((int(av_delay * fs), )), a_cue_pre), 0)
        
        vis_envelopes = []
        aud_envelopes = []
        
        # make envelopes and auditory stim
        aud_active = []
        for i, f in zip(np.arange(n_object), f0_trl):
            a_env = generate_noise(dur, fs, mod_fmin, mod_fmax, 1,
                                 'white') + env_offset
            aud_envelopes.append(a_env)
            noise = generate_harmonic_tone(dur, fs, f, n_harmonics, rms)
            noise_mod = a_env * noise
            noise_mod *= rms / np.std(noise_mod)
            noise_mod = window_edges(noise_mod, fs)
            if temp_coh[temp_idx]:
                env_ds = sig.resample(a_env, int(fps * dur)) / 4
            else: # make other vis env
                v_env = generate_noise(dur, fs, mod_fmin, mod_fmax, 1,
                                       'white') + env_offset
                env_ds = sig.resample(v_env, int(fps * dur)) / 4
                
            vis_envelopes.append(env_ds)
            
            if spat_cong[spat_idx]: # figure out where to put the sound
                sound_id = i
                n_trajectory = n_object
            else:
                sound_id = i + n_objects[-1]
                n_trajectory = 2 * n_object
            aud_path = os.path.join(stim_folder,
                                    'marble_planet_sound{}.ogg'.format(int(sound_id)))
            print('marble_planet_sound{}.ogg'.format(int(sound_id)))
            aud_active.append(sound_id)
            if i == target:
                sf.write(aud_path, np.concatenate((a_cue, noise_mod), 0), fs)
            else:
                sf.write(aud_path, np.concatenate((np.zeros(a_cue.shape),
                                                  noise_mod), 0), fs)
        vis_envelopes = np.array(vis_envelopes)
        aud_envelopes = np.array(aud_envelopes)      
        # make trajectories
        trajectories = np.zeros((n_trajectory, 3, len(env_ds)))
        for ii in np.arange(3):
            for i in np.arange(n_trajectory):
                trajectories[i, ii] = generate_noise(dur, fps, tr_f_min, 
                                                     tr_f_max, 0.01)
            
            trajectories[:, ii] *= (np.diff(bounds[ii]) / 
                                    (trajectories[:, ii].max() - 
                                     trajectories[:, ii].min()))
            trajectories[:, ii] += np.mean(bounds[ii])
        write_hdf5('stim_info_trl{}'.format(int(trl)) + ec.participant + '.hdf5',
                   dict(vis=vis_envelopes, aud=aud_envelopes, tra=trajectories), overwrite=True)
        # vis ready for cue
        [shape.set_sca(3 * [.1 * e + .1]) for shape, e in zip(shapes, vis_envelopes[:, 0])]
        shapes[target].set_visible(True)
        shapes[target + 6].set_visible(True)
        shapes[target].set_pos(trajectories[target, :, 0])
        shapes[target + 6].set_pos(trajectories[target, :, 0])
        
        for i in aud_active:
            client.send_message('/fname{}'.format(int(i)),
                                'marble_planet_sound{}.ogg'.format(int(i)))
            server.handle_request()
        client.send_message('/start_query', [0])
        server.handle_request()
        client.send_message('/Play', [0])
        
        start = ec.current_time
        ec.wait_until(start + av_delay)
        shapes[target].draw()
        shapes[target].send()
        shapes[target + 6].draw()
        shapes[target + 6].send()
#        [s.set_visible(True) for s in shapes[:n_object]]
        for i, (vis_env, traj) in enumerate(zip(vis_envelopes.T, 
                                             trajectories.transpose(2, 0, 1))):
            
            [shape.set_sca(3 * [.1 * e + .1]) for e, shape in zip(vis_env, 
                                                                  shapes[:n_object])]
            [shape.set_pos(tr) for tr, shape in zip(traj, shapes[:6])]
            [shape.set_pos(tr) for tr, shape in zip(traj[:3], shapes[6:])]
            [shape.draw() for shape in shapes]
            ec.wait_until(start + av_delay + cue_dur + (i + 1) / fps)
            [shape.send() for shape in shapes]
        ec.wait_secs(1)
        client.send_message('/Clear_audio', [0])
        #for i in aud_active:
        #    try:
        #        os.remove(stim_folder + 'marble_planet_sound{}.ogg'.format(int(i)))
        #    except:
        #        print('no file')