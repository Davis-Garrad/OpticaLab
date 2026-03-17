import numpy as np
import matplotlib.pyplot as plt

import time

from ray import Ray
import cfgs
from defines import *

from vecmath import rotate as rotvec

debug_level = int(cfgs.sargs['debug_level'])
max_depth = int(cfgs.sargs['max_depth'])

class State:
    '''A collection of Rays and a Scene. Can be operated on by the trace operator, and contains some nice functionality for saving etc.. Represents the state of the system at some timepoint.'''
    def __init__(self, scene, rays):
        self.scene = scene
        self.rays = rays
        total_intensity = 0
        for i in rays:
            total_intensity += i.intensity
        for i in rays:
            i.intensity /= total_intensity
        self.free_rays = [] # rays which will have no optical elements left in their path, and will only be traced in macro steps.
        self.dead_rays = [] # rays which will not be traced, but existed to create the final set of rays (self.rays)

    def show(self, ax=None, dead=True):
        '''dead shows the dead rays (progenitor rays)'''
        if(ax is None):
            fig, ax = plt.subplots(1,1)

        if(dead):
            for i in self.dead_rays:
                i.show(ax=ax)
        for i in self.free_rays:
            i.show(ax=ax)
        for i in self.rays:
            i.show(ax=ax)
        self.scene.show(ax=ax)
        ax.set_aspect('equal')
        left,right = ax.get_xlim()
        bottom,top = ax.get_ylim()
        height = top-bottom
        width = right-left
        vcentre = (top+bottom)/2.
        hcentre = (right+left)/2.
        
        dim = np.maximum(height, width)
        ax.set_xlim((hcentre-dim/2, hcentre+dim/2))
        ax.set_ylim((vcentre-dim/2, vcentre+dim/2))

        return ax

    def __str__(self):
        t = len(self.rays)+len(self.free_rays)+len(self.dead_rays)
        R = len(self.rays)/t
        F = len(self.free_rays)/t
        D = len(self.dead_rays)/t
        digs = int(np.max(np.ceil(np.log10([len(self.rays), len(self.free_rays), len(self.dead_rays)]))))
        return f'State: {t} rays, {len(self.rays):0>{digs}}/{len(self.free_rays):0>{digs}}/{len(self.dead_rays):0>{digs}} ({R*100:.0f}/{F*100:.0f}/{D*100:.0f}%) sim/free/dead'
