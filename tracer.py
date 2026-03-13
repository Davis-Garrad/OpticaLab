import numpy as np

import ray
import scene
import cfgs

import vecmath.rotate as rotvec

stepsize = float(cfgs.sargs['tracing_step'])

class State:
    '''A collection of Rays and a Scene. Can be operated on by the trace operator, and contains some nice functionality for saving etc.. Represents the state of the system at some timepoint.'''
    def __init__(self, scene, rays):
        self.scene = scene
        self.rays = rays

    def draw_static(self, ax):
        for i in self.rays:
            xs, ys = i.pos_record.get()
            ax.scatter(xs, ys, 'x')

    #TODO: Write saving/loading functionality.
    #TODO: Write an animation function for fun

def trace(state):
    '''Steps the rays forward by one timestep. Big guy'''

    # Algorithm is as follows:
    # 1. Determine the current and future positions (r, and r+stepsize*direction respectively)
    # 2. Determine if the current and future positions intersect objects
    #   - If they do, then perform 3. If not, skip to 4
    # 3. (interface) determine the current and future indices of refraction
    #   - Check current and future to see if they're inside objects
    #   - If either isn't, n=1. Else, n is determined by the object
    #   - Then, find new transmitted and reflected intensities & angles, change the ray direction, and generate a reflection ray if necessary. Increment the ray order.
    # 4. Step the ray forward.

    newrays = []
    for ray in state.rays:
        # step 1
        r = ray.pos
        rp = r + stepsize*ray.dir # prime
        
        # step 2
        int_r = state.scene.check_intersecting(r)
        int_rp = state.scene.check_intersecting(rp)

        if not(int_r is int_rp):
            # interface
            # step 3
            n_r  = int_r.index_x  if int_r  else 1 #TODO: birefringence
            n_rp = int_rp.index_x if int_rp else 1

            normal = int_r.get_normal(r, ray.dir) if int_r else int_rp.get_normal(r, ray.dir) #TODO: This is a bit weird, isn't it? Check on a better day.
            diff = ray.dir - normal
            incident_angle = np.atan2(diff[-1], diff[0])

            transmitted = ray.fresnel(n_r, n_rp, incident_angle)
            transmitted_angle = np.asin(n_r/n_rp * np.sin(incident_angle)) # Snell's law. # TODO: This can break - I should probably do this with wavevectors; after all, that's what I have. 
            reflected_angle = -incident_angle
            
            interface_pos = 1/2 * (r + rp) # best guess, not exact by any means. Will prevent the next ray from being "double" diffracted
            # reflected ray
            newrays += [ Ray(interface_pos, rotvec(-normal, reflected_angle), wavelength=ray.wavelength, polarisation=ray.polarisation, intensity=ray.intensity * (1-transmitted)) ]
            # transmitted ray
            newrays += [ Ray(interface_pos, rotvec(-normal, transmitted_angle), wavelength=ray.wavelength, polarisation=ray.polarisation, intensity=ray.intensity * transmitted) ]
        else:
            newrays += [ray]

        for i in newrays:
            i.step(stepsize)

        state.rays = newrays

