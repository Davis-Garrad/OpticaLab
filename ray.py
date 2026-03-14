import numpy as np
import matplotlib.pyplot as plt

import colours
import dguid
import cfgs
from defines import *

debug_level = int(cfgs.sargs['debug_level'])

class SmartRecord:
    def __init__(self, shape=(1,), initial_alloc=1024, block_size=1024, initial_record=None, initial_cursor=0):
        if(initial_record is None):
            self.rec = np.empty((initial_alloc,*shape))
        else:
            self.rec = initial_record
        self.cursor=initial_cursor
        self.block_size = block_size
    
    def push(self, val):
        if(self.cursor == self.rec.shape[0]-1):
            self.realloc()
        self.rec[self.cursor] = val
        self.cursor += 1

    def get(self):
        return self.rec[:self.cursor,...]

    def realloc(self):
        newblock = np.empty((self.block_size, *self.rec.shape[1:]))
        self.rec = np.concatenate((self.rec, newblock))

    def copy(self):
        return SmartRecord(self.rec.shape[1:], initial_alloc=0, block_size=self.block_size, initial_record=np.copy(self.rec), initial_cursor=self.cursor)

class Ray:
    def __init__(self, origin, direction, wavelength=532, polarisation='p', intensity=1, depth=0):
        '''Constructs a new Ray object, located at `origin` moving in `direction`. `wavelength` is in nanometers, default 532nm (green laser). `polarisation` should be "s" or "p". If `record` is provided, will retain a reference of that record; if not, will create a new record - useful for splitting one ray into two.'''
        self.id = dguid.get_uuid()
        if(debug_level >= DEBUG_ALL):
            print(f'Constructing ray at {origin} ({wavelength}nm) (id {self.id})')
        self.pos = origin
        self.dir = direction/np.sqrt(np.sum(np.square(direction)))
        self.col = wavelength
        self.intensity = intensity
        self.depth = depth # number of reflections/diffraction generations so far. (i.e., transmitted beam is same depth, first diffracted order is +1, etc.)
        self.pol = polarisation
        if not(self.pol == 's' or self.pol == 'p'):
            raise TypeError("You must specify either 's' or 'p' polarisation")

        self.pos_record = SmartRecord(shape=origin.shape)
        self.pos_record.push(self.pos)

    def step(self, stepsize):
        '''Steps the ray forward in it's direction, and records the new position'''
        self.pos += self.dir*stepsize
        self.pos_record.push(self.pos)

    def show(self, ax=None, color=None):
        '''2D for now.'''
        if(color is None):
            color = colours.wavelength_to_rgb(self.col)
        if(ax is None):
            plt.plot(self.pos_record.get()[:,0], self.pos_record.get()[:,-1], color=color, linewidth=1, alpha=self.intensity)
        else:
            ax.plot(self.pos_record.get()[:,0], self.pos_record.get()[:,-1], color=color, linewidth=1, alpha=self.intensity)

    def __str__(self):
        return f'Ray ({self.id} gen{self.depth}) - {self.col:.1f}nm, {self.intensity*100.:.2f}%{self.pol} xyz={self.pos} dir={self.dir}'
