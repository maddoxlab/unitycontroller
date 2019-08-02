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
import argparse
from pythonosc import udp_client, dispatcher, osc_server
import matplotlib.pyplot as plt


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

fs = 48000.
dispatcher = dispatcher.Dispatcher()
dispatcher.map('/start_ok', start_trial)

server = osc_server.BlockingOSCUDPServer((args_serve.ip, args_serve.port), 
                                         dispatcher)

with ExperimentController('test_unity', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          audio_controller=dict(TYPE='sound_card', 
                                                SOUND_CARD_API='ASIO',
                                                SOUND_CARD_BACKEND='rtmixer',
                                                SOUND_CARD_NAME='ASIO HDSPe FX',
                                                SOUND_CARD_FS=fs),
                          full_screen=False) as ec:
    
    shape = UnityShape(ec, client, 0, color=[0, 0, 0, 1], pos=[0, 0, 5], sca=[4.65, 4.6, 4.5])
    shape.draw()
    shape.send()

    while True:
        ec.load_buffer(np.repeat(np.r_[0.1, np.zeros(99)][np.newaxis, :], 2, 0))  # RMS == 0.01\
        shape.set_color([1, 1, 1, 1])
        shape.set_visible(1)
        shape.draw()
        
        client.send_message('/start_query', [0])
        server.handle_request()
        shape.send()
        start = ec.start_stimulus(start_of_trial=False, flip=False)
#        shape.set_color([0, 0, 0, 1])
        shape.set_visible(0)
        shape.draw()
        ec.wait_until(start + 5.5 / 90)
        shape.send()
        ec.wait_until(start + 1.)
        ec.stop()