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
from expyfun._utils import logger


class UnityShape(object):
    """Class for VR unity objects
    
    Parameters
    ----------
    ec :  instance of ExperimentController
        Parent EC.
    osc_client : instance of udpclient
        Parent OSC client.
        Usage as:
            
        # import argparse
        # from pythonosc import udp_client
        # parser = argparse.ArgumentParser()
        # parser.add_argument("--ip", default="127.0.0.1")
        # parser.add_argument("--port", type=int, default=5005)
        # args = parser.parse_args()

        # client = udp_client.SimpleUDPClient(args.ip, args.port)
    label : int
        index of the shape in unity -- must have matching ReceiveProperties 
        C# script with OSC and corresponding shape.
    pos : array-like
        3-element array-like with X, Y, and Z position.
    rot : array-like
        3-element array-like with X, Y, and Z rotation in degrees (0-360).
    sca : array-like
        3-element array-like with X, Y, and Z scale (>0).
    color : array-like
        4-element array-like with R, G, B, A values (0-1).
    visible : bool or int
        whether the shape is visible in unity 
        
    Returns
    -------
    unityshape : instance of UnityShape
        the Unity object
    """
    
    def __init__(self, ec, osc_client, label, pos=[0, 0, 1], rot=[0, 0, 0],
                 sca=[.2, .2, .2], color=[1, 1, 1, 1], visible=True):
        self._ec = ec
        self._osc_client = osc_client
        
        if not isinstance(label, int):
            raise ValueError('Label must be int')
            
        self._label = '/UnityShape' + str(label)
        
        if len(pos) != 3:
            raise ValueError('Must specify x, y, z position')
            
        self._pos = np.array(pos)
        
        if len(rot) != 3:
            raise ValueError('Must specify x, y, z rotation')
        if any(rot) > 360 or any(rot) < 0:
            raise ValueError('Rotation must be between 0 and 360 degrees')
        
        self._rot = np.array(rot)
        
        if len(sca) != 3:
            raise ValueError('Must specify x, y, z scale')
        if any(sca) < 0:
            raise ValueError('Scale must be larger than 0 meters')
        
        self._sca = np.array(sca)
        
        if len(color) != 4:
            raise ValueError('Must specify RGBA color')
        if any(color) > 1 or any(color) < 0:
            raise ValueError('RGBA values must be between 0 and 1')
        
        self._color = np.array(color)
        
        if type(visible) not in [int, bool]:
            raise ValueError('Visible must be bool or int')
        
        self._visible = np.array([visible], dtype=int)

    def set_pos(self, pos):
        """Update position
        
        Parameters
        ----------
        pos : array-like
            3-element array-like with X, Y, and Z position.
        """
        if len(pos) != 3:
            raise ValueError('Must specify x, y, z position')
        self._pos = np.array(pos)
    
    def set_rot(self, rot):
        """Update rotation
        
        Parameters
        ----------
        rot : array-like
            3-element array-like with X, Y, and Z rotation in degrees (0-360).
        """
        if len(rot) != 3:
            raise ValueError('Must specify x, y, z rotation')
        if any(rot) > 360 or any(rot) < 0:
            raise ValueError('Rotation must be between 0 and 360 degrees')
        
        self._rot = np.array(rot)
        
    def set_sca(self, sca):
        """Update scale
        
        Parameters
        ----------
        sca : array-like
            3-element array-like with X, Y, and Z scale (>0).
        """
        if len(sca) != 3:
            raise ValueError('Must specify x, y, z scale')
        if any(sca) < 0:
            raise ValueError('Scale must be larger than 0 meters')
        
        self._sca = np.array(sca)
    
    def set_color(self, color):
        """Update color
        
        Parameters
        ----------
        color : array-like
            4-element array-like with R, G, B, A values (0-1).
        """
        if len(color) != 4:
            raise ValueError('Must specify RGBA color')
        if any(color) > 1 or any(color) < 0:
            raise ValueError('RGBA values must be between 0 and 1')
            
        self._color = np.array(color)
    
    def set_visible(self, visible):
        """Update visibility
        
        Parameters
        ----------
        visible : bool or int
            whether the shape is visible in unity 
        """
        if type(visible) not in [int, bool]:
            raise ValueError('Visible must be bool or int')
        
        self._visible = np.array([visible])
    
    def draw(self):
        """Compiles parameters into an OSC message to send to Unity
        
        Notes: 
        Must be run before UnityShape.send()
        """
        self._message = np.concatenate([self._pos, self._rot, self._sca, 
                                        self._color, self._visible], 0)
    def send(self, blend_mode='add'):
        """Send parameters to Unity
        
        Notes: 
        Must be run UnityShape.draw() first
        """
        self._osc_client.send_message(self._label, np.array(self._message, dtype=float))
            
