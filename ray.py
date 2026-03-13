import numpy as np
import matploblib.pyplot as plt

import dguid

class SmartRecord:
    def __init__(self, shape=(1,), initial_alloc=1024, block_size=1024):
        self.rec = np.empty((initial_alloc,*shape))
        self.cursor=0
        self.block_size = block_size
    
    def push(self, val):
        if(self.cursor > self.rec.shape[0]):
            self.realloc()
        self.rec[cursor] = val
        cursor += 1

    def get(self):
        return self.rec[:cursor]

    def realloc(self):
        self.rec = np.append(self.rec, np.empty((self.block_size, *self.rec.shape[1:])))

class Ray:
    def __init__(self, origin, direction, wavelength=532, polarisation='p', intensity=1, record=None):
        '''Constructs a new Ray object, located at `origin` moving in `direction`. `wavelength` is in nanometers, default 532nm (green laser). `polarisation` should be "s" or "p". If `record` is provided, will retain a reference of that record; if not, will create a new record - useful for splitting one ray into two.'''
        self.id = dguid.get_uuid()
        print(f'Constructing ray at {origin} ({wavelength}nm) (id {self.id})')
        self.pos = origin
        self.dir = direction
        self.col = wavelength
        self.intensity = intensity
        self.depth = 0 # number of reflections/diffraction generations so far. (i.e., transmitted beam is same depth, first diffracted order is +1, etc.)
        self.pol = polarisation
        if not(self.pol == 's' or self.pol == 'p'):
            raise TypeError("You must specify either 's' or 'p' polarisation")

        if(record is None):
            self.pos_record = SmartRecord(shape=origin.shape)
        else: 
            self.pos_record = record

    def step(self, stepsize):
        '''Steps the ray forward in it's direction, and records the old position'''
        self.pos_record.push(self.pos)
        self.pos += self.dir*stepsize

    def show(self, ax=None, color='g'):
        '''2D for now.'''
        if(ax is None):
            plt.plot(self.pos_record.get()[0], self.pos_record.get()[1], color=color)

    def fresnel(self, index_0, index_1, angle_0):
        '''Returns the transmitted intensity, based on Fresnel equations. angle_0 is measured from the normal, and the indices are indices of refraction. We only care about the intensity; this is geometric optics. Reflected intensity is of course 1-T'''

        cos_thetat = np.sqrt(complex(1 - np.square(index_0/index_1 * np.sin(angle_0))), dtype=complex)
        cos_theta0 = np.cos(angle_0)

        if(self.pol == 's'):
            reflected = np.square(np.abs((index_0*cos_theta0 - index_1*cos_thetat)/(index_0*cos_theta0 + index_1*cos_thetat)))
        else:
            reflected = np.square(np.abs((index_0*cos_thetat - index_1*cos_theta0)/(index_0*cos_thetat + index_1*cos_theta0)))

        return reflected

