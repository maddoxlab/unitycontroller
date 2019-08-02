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
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

frames = 300

with ExperimentController('test_unity', output_dir=None, version='dev', 
                          participant='foo', session='foo', stim_fs=48000,
                          force_quit=['end', 'lctrl'],
                          full_screen=False) as ec:
    shapes = [UnityShape(ec, client, int(i)) for i in np.arange(5)]

    shapes[1].set_pos([-1, 0, 2])
    shapes[2].set_pos([1, 0, 2])
    shapes[0].set_color([0, 1, 1, 1])
    shapes[1].set_color([1, .75, 0, 1])
    shapes[-2].set_color([.5, 0, 1, 1])
    shapes[-2].set_sca([.1, .1, .1])
    shapes[-1].set_color([1, 0, .2, 1])
    shapes[-1].set_sca([.05, .05, .05])

    theta = np.radians(np.linspace(-180, 180.2, frames))
    pos_0 = np.zeros((frames, 3))
    pos_0[:, 0] = np.sin(theta)
    pos_0[:, -1] = np.cos(theta)
    pos_3 = np.roll(pos_0, 15, 0)
    pos_4 = np.roll(pos_0, 30, 0)
    
    rot_1 = np.zeros((frames, 3))
    rot_1[:, -1] = np.linspace(0, 360, frames)
    
    cm = plt.get_cmap('magma')
    color_2 = cm(np.linspace(0, 1, frames // 2, dtype=float)) 
    color_2 = np.concatenate((color_2, np.flipud(color_2)), 0)
    start = ec.current_time
    while True:
        for p, r, c, p3, p4 in zip(pos_0, rot_1, color_2, pos_3, pos_4):
            
            shapes[0].set_pos(p)
            shapes[1].set_rot(r)
            shapes[2].set_color(c)
            shapes[-2].set_pos(p3)
            shapes[-1].set_pos(p4)
            
            [s.draw() for s in shapes]
            ec.wait_until(start + .01)
            [s.send() for s in shapes]
            start = ec.current_time