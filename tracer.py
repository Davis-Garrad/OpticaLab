import numpy as np

import ray
import scene
import cfgs

class State:
    '''A collection of Rays and a Scene. Can be operated on by the trace operator, and contains some nice functionality for saving etc.. Represents the state of the system at some timepoint.'''
    def __init__(self, scene, rays):
        self.scene = scene
        self.rays = rays

    #TODO: Write saving/loading functionality.
    #TODO: Write an animation function for fun

def trace(state):
    '''Steps the rays forward by one timestep. Big guy'''
