import numpy as np

import matplotlib.pyplot as plt

import ray
import scene

class Sensor:
    '''Defines a sensor plane. Basically just counts the rays which intersect the plane defined by position0 and position1'''
    def __init__(self, position0, position1):
        self.pos0 = position0
        self.pos1 = position1
        self.width = np.sqrt(np.sum(np.square(self.pos0 - self.pos1)))

    def intensity(self, state):
        intensity = 0
        for r in self.get_intersecting_rays(state):
            intensity += r.intensity

        return intensity

    def get_intensity_pattern(self, state):
        '''Gets the (approximate) intensity map across the sensor. Returns a 1D array'''
        # get appropriate rays
        rays = self.get_intersecting_rays(state)
        if(len(rays) == 0):
            return [0], [0]

        # sweep a small window
        smoothing_factor = 1 # yeah, yeah, magic number, yeah yeah. TODO: implement properly
        overlap = 0.9 # approximate overlap between windows.
        final_resolution = len(rays)
        resolution = final_resolution*int(np.ceil(smoothing_factor / (1-overlap))) # defines the smallest bin size.
        window_size = self.width/(final_resolution*smoothing_factor)
        i = 0
        translations = np.linspace(0, self.width, resolution)
        intensity_map = np.zeros_like(translations)
        for x in translations:
            # create a new sensor and use that for calculations
            c0 = self.pos0 + x*(self.pos1-self.pos0)/self.width
            c1 = c0 + window_size*(self.pos1-self.pos0)/self.width
            s = Sensor(c0, c1)
            intensity_map[i] += s.intensity(state)
            i += 1

        # smoothing pass
        if(True):
            intensity_map = np.reshape(intensity_map, (final_resolution, int(np.ceil(smoothing_factor/(1-overlap)))))
            intensity_map = np.average(intensity_map, axis=1)
            translations = np.average(np.reshape(translations, (final_resolution, int(np.ceil(smoothing_factor/(1-overlap))))), axis=1)

        return translations-self.width/2, intensity_map

    def show(self, ax=None):
        if(ax is None):
            fig, ax = plt.subplots(1,1)
        ax.plot([self.pos0[0], self.pos1[0]], [self.pos0[-1], self.pos1[-1]], linestyle='dotted', linewidth=4, color='k', marker='D', markersize=4)
        return ax

    def get_intersecting_rays(self, state):
        '''Returns a list of all rays which are guaranteed to intersect the sensor plane'''
        rays = state.rays + state.free_rays + state.dead_rays # all rays should be counted.
        intersecting = []
        # this is easy since all the rays are straight lines!
        for r in rays:
            c0 = self.pos0 - r.origin
            c1 = self.pos1 - r.origin
            d0 = self.pos0 - r.pos
            d1 = self.pos1 - r.pos
            direc = r.pos - r.origin # this is really just r.dir, but who cares
            perp = np.array([direc[-1], direc[1], -direc[0]])

            in_view = (np.sign(np.dot(perp, c0)) == -np.sign(np.dot(perp, c1)))
            
            intersect_plane=self.pos1-self.pos0
            intersect_normal=np.array([intersect_plane[-1], intersect_plane[1], -intersect_plane[0]])
            passed = (np.sign(np.dot(intersect_normal, c0)) != np.sign(np.dot(intersect_normal, d0)))

            if(passed and in_view):
                intersecting += [r]
        return intersecting
