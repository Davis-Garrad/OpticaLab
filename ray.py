import numpy as np
import matploblib.pyplot as plt

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
    def __init__(self, origin, direction, wavelength=532):
        '''Constructs a new Ray object, located at `origin` moving in `direction`. `wavelength` is in nanometers, default 532nm (green laser).'''
        print(f'Constructing ray at {origin} ({wavelength}nm)')
        self.pos = origin
        self.dir = direction
        self.col = wavelength
        self.depth = 0 # number of reflections/diffraction generations so far. (i.e., transmitted beam is same depth, first diffracted order is +1, etc.)

        self.pos_record = SmartRecord(shape=origin.shape)

    def show(self, ax=None, color='g'):
        '''2D for now.'''
        if(ax is None):
            plt.plot(self.pos_record.get()[0], self.pos_record.get()[1], color=color)
