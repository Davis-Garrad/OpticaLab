import numpy as np

import ray
import scene

class Sensor:
    '''Defines a sensor plane. Basically just counts the rays which intersect the plane defined by position0 and position1'''
    def __init__(self, position0, position1):
        self.pos0 = position0
        self.pos1 = position1

    def intensity(self, state):
        intensity = 0
        rays = state.rays + state.free_rays + state.dead_rays # all rays should be counted.

        # intersecting pass.
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
                intensity += r.intensity

        return intensity

    def show(self, ax=None):
        if(ax is None):
            fig, ax = plt.subplots(1,1)
        ax.plot([self.pos0[0], self.pos1[0]], [self.pos0[-1], self.pos1[-1]], linestyle='dotted', linewidth=4, color='k', marker='D', markersize=4)
        return ax
