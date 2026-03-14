import numpy as np
import matplotlib.pyplot as plt

from ray import Ray
import cfgs
from defines import *

from vecmath import rotate as rotvec

stepsize = float(cfgs.sargs['tracing_step'])
debug_level = int(cfgs.sargs['debug_level'])
max_depth = int(cfgs.sargs['max_depth'])

class State:
    '''A collection of Rays and a Scene. Can be operated on by the trace operator, and contains some nice functionality for saving etc.. Represents the state of the system at some timepoint.'''
    def __init__(self, scene, rays):
        self.scene = scene
        self.rays = rays
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

        return ax

    #TODO: Write saving/loading functionality.
    #TODO: Write an animation function for fun

def fresnel(polarisation, index_0, index_1, cos_theta0, cos_thetat):
    '''Gets the reflected (1-transmitted) intensity'''
    if(polarisation == 's'):
        reflected = np.square(np.abs((index_0*cos_theta0 - index_1*cos_thetat)/(index_0*cos_theta0 + index_1*cos_thetat)))
    else:
        reflected = np.square(np.abs((index_0*cos_thetat - index_1*cos_theta0)/(index_0*cos_thetat + index_1*cos_theta0)))

    return reflected

def trace(state, resolution=1000, macrostepsize=1):
    '''Steps the rays forward by one macrostep. Big guy.
    `resolution` defines the smallest stepsize which should be taken as rays approach objects as macrostepsize/resolution.
    `macrostepsize` defines the distance that the rays should march after determining they're close to objects, before performing another optimising step. Broadly, this value should reflect the average width of optical elements. This is the minimum distance that rays will march with one call of this function. There is, in general, no maximum, as long as optical elements exist in front of the rays.'''

    # Algorithm is as follows:
    # 0 (PRE-COMPUTING). For each ray; Find the next obstacle in a straight line (closest edge distance, O(n*m) object calculations for n objects, m resolution), and move the ray nearby
    # 1. Determine the current and future positions (r, and r+stepsize*direction respectively)
    # 2. Determine if the current and future positions intersect objects
    #   - If they do, then perform 3. If not, skip to 4
    # 3. (interface) determine the current and future indices of refraction
    #   - Check current and future to see if they're inside objects
    #   - If either isn't, n=1. Else, n is determined by the object
    #   - Then, find new transmitted and reflected intensities & angles, change the ray direction, and generate a reflection ray if necessary. Increment the ray order.
    # 4. Step the ray forward.
    #print(f'Tracer step ({stepsize})')

    stepsize = macrostepsize/resolution

    #step 0, to avoid long ray marching steps in between optical elements.
    newrays = []
    for ray in state.rays:
        closest_pt,sqrdist = state.scene.get_nextinterface(ray.pos, ray.dir) # searches by max radius
        if(closest_pt is None):
            if(sqrdist is None): # no more elements to hit! Free Ray!
                state.free_rays += [ray]
            elif(sqrdist == 0): # we're already too close to optimise anything.
                newrays += [ray]
        else:
            if(sqrdist > np.square(stepsize)):
                ray.pos += ray.dir * (np.sqrt(sqrdist) - stepsize)
                newrays += [ray]
            # else, we're already close enough that we might cross an interface with this optimisation. Same-ish as case 2 above.
    state.rays = newrays

    for ray in state.free_rays:
        # macro step! ezpz.
        ray.step(macrostepsize)
    
    for run_i in range(resolution):
        newrays = []
        for ray in state.rays:
            # step 1
            r = ray.pos
            rp = r + stepsize*ray.dir # expected location

            # step 2
            int_r = state.scene.check_intersecting(r)
            int_rp = state.scene.check_intersecting(rp)
            if(debug_level >= DEBUG_ALL):
                print(ray, int_r, int_rp)

            if not(int_r is int_rp):
                # interface
                # step 3
                n_r  = int_r.index_x  if int_r  else 1. #TODO: birefringence
                n_rp = int_rp.index_x if int_rp else 1.

                nratio = n_r/n_rp

                normal = int_r.get_normal(r, ray.dir) if int_r else int_rp.get_normal(r, ray.dir) #TODO: This is a bit weird, isn't it? Check on a better day.
                #incident_angle = np.abs(np.atan2(normal[-1],normal[0]) - np.atan2((-ray.dir)[-1], (-ray.dir)[0]))

                #if not(-np.pi/2 < incident_angle < np.pi/2):
                #    print(incident_angle * 180/np.pi)
                #    incident_angle = np.fmod(incident_angle, np.pi/2)

                #transmitted_angle = np.asin(n_r/n_rp * np.sin(incident_angle)) # Snell's law. # TODO: This can break - I should probably do this with wavevectors; after all, that's what I have. 
                #reflected_angle = -incident_angle

                cos_incident = -np.dot(normal, ray.dir)
                reflected_dir = ray.dir + 2*cos_incident * normal

                if(np.square(nratio)*(1-np.square(cos_incident)) < 1):
                    cos_refracted = np.sqrt(1-np.square(nratio)*(1-np.square(cos_incident)))
                    transmitted_dir = nratio * ray.dir + (nratio * cos_incident - cos_refracted)*normal
                    
                    transmitted = 1-fresnel(ray.pol, n_r, n_rp, cos_incident, cos_refracted)
                else:
                    transmitted=0

                state.dead_rays += [ray] # signal that we should NOT trace this!

                if(ray.depth == max_depth): # in this case, only one should survive!
                    if(transmitted > 0.5): # transmitted dominant
                        newrays += [ Ray(r, reflected_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * (1-transmitted), depth=ray.depth) ]
                    else:
                        newrays += [ Ray(r, reflected_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * (1-transmitted), depth=ray.depth) ]
                else:
                    # reflected ray
                    if(transmitted < 1):
                        newrays += [ Ray(r, reflected_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * (1-transmitted), depth=ray.depth+1) ]
                    # transmitted ray
                    if(transmitted > 0):
                        newrays += [ Ray(rp, transmitted_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * transmitted, depth=ray.depth+1) ]
            else:
                newrays += [ray]

        for i in newrays:
            i.step(stepsize)

        state.rays = newrays

