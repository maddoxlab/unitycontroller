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

# Experiment parameters
fs = 48000
f_max = np.logspace(11, 12, 5, base=2)
visfs = 90
radius = 1
mod_fs = 5
n_objects = 5
dur = 10
stim_folder = "C:\\Users\\mcappelloni\\Sandbox2\\Assets\\Resources\\"

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

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1")
parser.add_argument("--port", type=int, default=5005)
args_client = parser.parse_args()

client = udp_client.SimpleUDPClient(args_client.ip, args_client.port)

start_ok = False

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
server.timeout = 1

with ExperimentController('test_unity', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          full_screen=False) as ec:

    shapes = [UnityShape(ec, client, int(i)) for i in np.arange(5)]

    [shape.set_pos([-1, 1, 100]) for shape in shapes]
    [shape.set_color([1, 1, 1, 1]) for shape in shapes]
    [shape.set_sca([.1, .1, .1]) for shape in shapes]
    
    eTime = np.arange(fs * dur) / fs
    
    vis_envelopes = []
    for i, f in zip(np.arange(n_objects), f_max):
        env = generate_noise(dur, fs, 0.1, 5, 1, 'white') + 2
        #env = np.cos(2 * np.pi * mod_fs * eTime) + 4
        noise = generate_noise(dur, fs, f / 4, f, 0.01, 'pink')
        noise_mod = env * noise
        noise_mod *= 0.01/np.std(noise_mod)
        noise_mod = window_edges(noise_mod, fs)
        
        env_ds = sig.resample(env, visfs * 10) / 4
        vis_envelopes.append(env_ds)
        
        aud_path = os.path.join(stim_folder,'noise_mod{}.ogg'.format(int(i)))
        sf.write(aud_path, noise_mod, fs)
    vis_envelopes = np.array(vis_envelopes).T
    vis_path = os.path.join(stim_folder,'vis_envelopes.hdf5')
    write_hdf5(vis_path, vis_envelopes, overwrite=True)

    env_ds = sig.resample(env, visfs * 10) / 2
    pos = np.zeros((n_objects, len(env_ds), 3))
    pos[:, :, -1] = 1
    theta = np.radians(np.linspace(-180, 180.2, len(env_ds)))
    pos[0, :, 0] = np.sin(theta) * radius
    pos[0, :, -1] = np.cos(theta) * radius
    pos[1, :, 1] = np.sin(theta) * radius
    pos[1, :, 0] = np.cos(theta) * radius
    pos[2] = np.roll(pos[1], 20, 0)
    pos[3] = np.flipud(pos[2])
    pos[3, :, -1] += 2 
    pos[4] = pos[2] *.5
    pos[4, :, -1] += 2
    pos[1, :, -1] += 3
    
    while True:
#        ec.load_buffer(noise_mod)
        for i in np.arange(n_objects):
            client.send_message('/fname{}'.format(int(i)),
                                'noise_mod{}.ogg'.format(int(i)))
            server.handle_request()
        client.send_message('/start_query', [0])
        server.handle_request()
        client.send_message('/Play', [0])
        start = ec.current_time
#        start = ec.start_stimulus(start_of_trial=False, flip=False)
        
        for i, (vis_env, p) in enumerate(zip(vis_envelopes, pos.transpose(1, 0, 2))):
            
            [shape.set_sca(3 * [.1 * e + .1]) for e, shape in zip(vis_env, shapes)]
            [shape.set_pos(po) for po, shape in zip(p, shapes)]
            [shape.draw() for shape in shapes]
            ec.wait_until(start + (i + 1) / visfs)
            [shape.send() for shape in shapes]
