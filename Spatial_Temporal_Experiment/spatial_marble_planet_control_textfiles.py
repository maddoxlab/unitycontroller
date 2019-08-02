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
from expyfun.io import write_hdf5, read_hdf5
import argparse
from pythonosc import udp_client, dispatcher, osc_server
import matplotlib.pyplot as plt
import scipy.signal as sig
#import soundfile as sf
from scipy.io import wavfile
import os
#from pathlib import Path
 
# %% SETUP
# Experiment parameters

# General
n_trl = 12
n_objects = [1, 3]
n_max_obj = 3
spat_cong = [1]
temp_coh = [1]
#n_objects = [3]
#spat_cong = [1]
#temp_coh = [1]
dur = 10 #9.15
mod_fmin = 0.1
mod_fmax = 5
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
ring_size = .1
vis_size = .01
vis_scale = .07
ring_color = [.0, .0, .0, 1]
colors = [[1., .75, .25], [.25, 1., .75], [.75, .25, 1.]]

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
def response(address, *args):
    print(args)
    args[0][0].write_data_line("response [vis, aud]", list(args[1:]), args[0][0].current_time)
    
    
dispatcher = dispatcher.Dispatcher()
dispatcher.map('/start_ok', start_trial)
dispatcher.map('/loaded', loaded)


server = osc_server.BlockingOSCUDPServer((args_serve.ip, args_serve.port), 
                                         dispatcher)
server.timeout = 3

# %% load in data
data = read_hdf5('stimulus_data.hdf5')
aud_env = data['aud_env']
trajectories = data['trajectories']
vis_env_coh = data['vis_env_coh']
vis_env_incoh = data['vis_env_incoh']
vis_stim = data['vis_stim']
rotation = data['rotation']

# %% Set trial order
trl_ID = np.random.permutation(np.arange(n_trl))

# %% EC
with ExperimentController('test_unity', version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          full_screen=False) as ec:
    dispatcher.map('/response', response, ec)
    shapes = [UnityShape(ec, client,
                         int(i)) for i in np.arange(n_objects[-1] * 3)]
    [s.set_rot([-90, 0, 0]) for s in shapes[2 * n_max_obj:]]
    ec.wait_secs(5)
    for trl in trl_ID:
        # figure out which condition
        spat_idx = trl % len(spat_cong)
        temp_idx = (trl // len(spat_cong)) % len(temp_coh)
        n_obj_idx = ((trl // len(spat_cong)) // len(temp_coh)) % len(n_objects)
        
        n_obj_trl = n_objects[n_obj_idx]
        aud_active = np.arange(n_obj_trl)
        
        if temp_coh[temp_idx]:
            vis_env = vis_env_coh[trl]
        else:
            vis_env = vis_env_incoh[trl]
        # shuffle colors
        
        if spat_cong[spat_idx]:
            active_trajectories = np.arange(n_obj_trl)
        else:
            active_trajectories = np.concatenate((np.arange(n_obj_trl), 
                                                  n_max_obj + np.arange(n_obj_trl)), 0)
        colors = np.random.permutation(colors)
        
        # choose n_object condition
        n_object = n_objects[n_obj_idx]
        [s.set_sca(3 * [0]) for s in shapes]
        [s.set_color(np.concatenate((c, [1]), 0)) for s, c in zip(shapes[:n_max_obj], colors)]
        [s.set_color(ring_color) for s in shapes[2 * n_max_obj:]]
        [s.draw() for s in shapes]
        [s.send() for s in shapes]
        
        # randomly set f0's
        f0_trl = np.array(np.random.choice(f0, (n_object,), replace=False))
        
        # pick which one will be the target
        target = np.random.randint(0, n_object)
        
        # vis ready for cue
        [shape.set_sca(3 * [vis_scale * e + vis_size]) for shape, e in zip(shapes, vis_env[:n_obj_trl, 0])]
        shapes[target].set_pos(trajectories[trl, target, :, 0])
        shapes[target + 2 * n_max_obj].set_pos(trajectories[trl, target, :, 0])
        shapes[target + 2 * n_max_obj].set_rot([-rotation[trl, target, 1, 1], rotation[trl, target, 0, 0], 0])
        shapes[target + 2 * n_max_obj].set_sca(3 * [ring_size])
        shapes[target].draw()
        shapes[target + 2 * n_max_obj].draw()

        client.send_message('/fname{}'.format(target), 'cue_{}'.format(f0[target]))
        server.handle_request()
        
        client.send_message('/start_query', [0])
        server.handle_request()
        
        client.send_message('/Play', [0])
        
        shapes[target].send()
        shapes[target + 2 * n_max_obj].send()
        [s.set_sca(3 * [ring_size]) for s in shapes[2 * n_max_obj:2 * n_max_obj + n_obj_trl]]
        cue_start = ec.current_time
        ec.wait_until(cue_start + cue_dur)
        for i in aud_active:
            if spat_cong[spat_idx]:
                address = '/fname{}'.format(i)
            else:
                address = '/fname{}'.format(i + n_max_obj)
            client.send_message(address,
                                'A_trl_{}_obj_{}.wav'.format(int(trl), int(i)))
            server.handle_request()
        ec.wait_until(cue_start + cue_dur + .2)
        client.send_message('/start_query', [0])
        server.handle_request()
        
        client.send_message('/Play', [0])
        
        start = ec.current_time
        ec.write_data_line("trial_started", start)
        ec.wait_until(start + av_delay)

        for i, (v_e, v_s, traj, rot) in enumerate(zip(vis_env.T,
                                                      vis_stim[trl].transpose(1, 0),
                                            trajectories[trl].transpose(2, 0, 1),
                                            rotation[trl].transpose(2, 0, 1))):
            [shapes[a].set_sca(3 * [vis_scale * e + vis_size]) for e, a in zip(v_e, np.arange(n_obj_trl))]
            [shapes[a].set_pos(traj[a]) for a in active_trajectories]
            [s.set_pos(tr) for tr, s in zip(traj[:n_obj_trl], shapes[(2 * n_max_obj):(2 * n_max_obj + n_obj_trl)])]
            [s.set_rot([-r[1], r[0], 0]) for r, s in zip(rot[:n_obj_trl], shapes[(2 * n_max_obj):(2 * n_max_obj + n_obj_trl)])]
            [s.set_color(np.concatenate((v * c, [1]), 0)) for v, s, c in zip(v_s[:n_obj_trl], shapes[:n_obj_trl], colors[:n_obj_trl])]
            [s.draw() for s in shapes]
            ec.wait_until(start + av_delay + (i + 1) / fps)
            [s.send() for s in shapes]
#        [s.set_visible(True) for s in shapes[:n_object]]
#        for i, (vis_env, traj) in enumerate(zip(vis_envelopes.T, 
#                                             trajectories.transpose(2, 0, 1))):
#            
#            [shape.set_sca(3 * [.1 * e + .1]) for e, shape in zip(vis_env, 
#                                                                  shapes[:n_object])]
#            [shape.set_pos(tr) for tr, shape in zip(traj, shapes[:6])]
#            [shape.set_pos(tr) for tr, shape in zip(traj[:3], shapes[6:])]
#            [shape.draw() for shape in shapes]
#            ec.wait_until(start + av_delay + cue_dur + (i + 1) / fps)
#            [shape.send() for shape in shapes]
        server.handle_request()
        ec.wait_secs(1)
        client.send_message('/Clear_audio', [0])
        #for i in aud_active:
        #    try:
        #        os.remove(stim_folder + 'marble_planet_sound{}.ogg'.format(int(i)))
        #    except:
        #        print('no file')