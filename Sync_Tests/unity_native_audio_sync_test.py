# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 07:51:02 2019

@author: mcappelloni
"""

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
import soundfile as sf


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

fs = 48000
dispatcher = dispatcher.Dispatcher()
dispatcher.map('/start_ok', start_trial)
dispatcher.map('loaded', loaded)

server = osc_server.BlockingOSCUDPServer((args_serve.ip, args_serve.port), 
                                         dispatcher)
server.timeout = 5.

with ExperimentController('unity_native_sync', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=fs,
                          force_quit=['end', 'lctrl'],
                          audio_controller=dict(TYPE='sound_card', 
                                                SOUND_CARD_API='ASIO',
                                                SOUND_CARD_BACKEND='rtmixer',
                                                SOUND_CARD_NAME='ASIO HDSPe FX',
                                                SOUND_CARD_FS=fs),
                          full_screen=False) as ec:
    
    
    sound = np.r_[1, np.zeros(999)]
    sf.write("C:\\Users\\mcappelloni\\AV Sync Test\\Assets\\Resources\\sync.ogg",
             sound, fs)
    shape = UnityShape(ec, client, 0, color=[1, 1, 1, 1],
                       pos=[0, 0, 5], rot=[-90, 0, 0], sca=[10, 10, 10])
    shape.draw()
    shape.send()

    while True:
        shape.set_visible(1)
        shape.draw()
        client.send_message('/fname0', 'sync.ogg')
        server.handle_request()
        client.send_message('/start_query', [0])
        server.handle_request()
        client.send_message('/Play', [0])
        start = ec.current_time
        shape.send()
        shape.set_visible(0)
        shape.draw()
        ec.wait_until(start + 5.5 / 90)
        shape.send()
        ec.wait_until(start + 1.)