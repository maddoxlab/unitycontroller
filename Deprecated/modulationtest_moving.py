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
import argparse
from pythonosc import udp_client, dispatcher, osc_server
import matplotlib.pyplot as plt
import scipy.signal as sig
from scipy.io.wavfile import write

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
    
dispatcher = dispatcher.Dispatcher()
dispatcher.map('/start_ok', start_trial)

server = osc_server.BlockingOSCUDPServer((args_serve.ip, args_serve.port), 
                                         dispatcher)

server.timeout = 1
fs = 48000
visfs = 90

with ExperimentController('test_unity', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          full_screen=False) as ec:

    shape = UnityShape(ec, client, 0)

    shape.set_pos([0, .5, 1])
    shape.set_color([1, 1, 1, 1])
    shape.set_sca([.1, .1, .1])
    
    eTime = np.arange(fs * 10) / fs
    env = np.cos(2 * np.pi * 5 * eTime) + 2
    noise = np.random.rand(env.shape[0])
    noise_mod = env * noise
    noise_mod *= 0.01/np.std(noise_mod)
    noise_mod = window_edges(noise_mod, fs)
    
    write('noise_mod.wav', fs, noise_mod)
    env_ds = sig.resample(env, visfs * 10) / 2
    
    
    while True:
#        ec.load_buffer(noise_mod)
        
        client.send_message('/start_query', [0])
        server.handle_request()
        client.send_message('/Play', [0])
        start = ec.current_time
#        start = ec.start_stimulus(start_of_trial=False, flip=False)
        
        for i, e in enumerate(env_ds):
            
            shape.set_pos
            shape.set_sca(3 * [.1 * e])

            shape.draw()
            ec.wait_until(start + (i + 1) / visfs)
            shape.send()
            
        ec.wait_secs(1)
        ec.stop()