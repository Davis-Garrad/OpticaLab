import numpy as np
import matplotlib.pyplot as plt

import time

from ray import Ray
import state
import cfgs
from defines import *

from vecmath import rotate as rotvec

debug_level = int(cfgs.sargs['debug_level'])
max_depth = int(cfgs.sargs['max_depth'])

def status_update(s, clr=50):
    print(f'\r{s:<{clr}}\r', end='')

def fresnel(polarisation, index_0, index_1, cos_theta0, cos_thetat):
    '''Gets the reflected (1-transmitted) intensity'''
    if(polarisation == 's'):
        reflected = np.square(np.abs((index_0*cos_theta0 - index_1*cos_thetat)/(index_0*cos_theta0 + index_1*cos_thetat)))
    else:
        reflected = np.square(np.abs((index_0*cos_thetat - index_1*cos_theta0)/(index_0*cos_thetat + index_1*cos_theta0)))

    return reflected


def trace(state, stepsize=1, resolution=1000):
    '''Steps the rays forward by one macrostep. Big guy.
    `resolution` defines the smallest stepsize which should be taken as rays approach objects as 1/resolution.
    `stepsize` defines the (minimum) distance that the (free and finely-stepped) rays should march. There is, in general, no maximum for rays which still have elements in front of them.'''

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

    if(debug_level >= DEBUG_MIN):
        st = time.time()

    u_stepsize = 1./resolution # microstepsize

    #step 0, to avoid long ray marching steps in between optical elements.
    newrays = []
    status_update('Starting jump optimisation')
    for ray_i in range(len(state.rays)):
        ray = state.rays[ray_i]
        closest_pt,propdist = state.scene.get_nextinterface(ray.pos, ray.dir) # searches by max radius
        if(closest_pt is None):
            if(propdist is None): # no more elements to hit! Free Ray!
                state.free_rays += [ray]
            elif(propdist == 0): # we're already too close to optimise anything.
                newrays += [ray]
        else:
            if(propdist > np.square(u_stepsize)):
                ray.step(propdist - u_stepsize)
                newrays += [ray]
            # else, we're already close enough that we might cross an interface with this optimisation. Same-ish as case 2 above.
        status_update(f'Jump optimisation: {ray_i}/{len(state.rays)}')
    state.rays = newrays

    status_update('Jumping')
    for ray in state.free_rays:
        # macro step! ezpz.
        ray.step(stepsize)
    
    status_update('Starting raymarch')
    Nruns = int(resolution * stepsize)
    for run_i in range(Nruns):
        newrays = []
        for ray_i in range(len(state.rays)):
            ray = state.rays[ray_i]
            # step 1
            r = ray.pos
            rp = r + u_stepsize*ray.dir # expected location

            # step 2
            int_r = state.scene.check_intersecting(r)
            int_rp = state.scene.check_intersecting(rp)
            if(debug_level >= DEBUG_ALL):
                print(ray, int_r, int_rp)

            if not(int_r is int_rp):
                # interface
                # step 3
                n_r  = int_r.get_index(ray.col)  if int_r  else 1. #TODO: birefringence
                n_rp = int_rp.get_index(ray.col) if int_rp else 1.

                nratio = n_r/n_rp

                normal = int_r.get_normal(r, ray.dir) if int_r else int_rp.get_normal(r, ray.dir)

                cos_incident = -np.dot(normal, ray.dir)
                reflected_dir = ray.dir + 2*cos_incident * normal

                if(np.square(nratio)*(1-np.square(cos_incident)) < 1):
                    cos_refracted = np.sqrt(1-np.square(nratio)*(1-np.square(cos_incident)))
                    transmitted_dir = nratio * ray.dir + (nratio * cos_incident - cos_refracted)*normal
                    
                    transmitted = 1-fresnel(ray.pol, n_r, n_rp, cos_incident, cos_refracted)
                else:
                    transmitted=0
                if(np.isnan(transmitted)): # This is a limiting case, when nratio goes to inf or zero. This leads to other calculations breaking, but I'm frankly too lazy to change the whole form of said calculations....
                    transmitted = 0
                state.dead_rays += [ray] # signal that we should NOT trace this!

                if(ray.depth+1 <= max_depth or max_depth==-1):
                    # reflected ray
                    if(transmitted < 1):
                        newrays += [ Ray(r, reflected_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * (1-transmitted), depth=ray.depth+1) ]
                    # transmitted ray
                    if(transmitted > 0):
                        newrays += [ Ray(rp, transmitted_dir, wavelength=ray.col, polarisation=ray.pol, intensity=ray.intensity * transmitted, depth=ray.depth+1) ]
            else:
                newrays += [ray]
        status_update(f'Raymarch: {run_i}/{Nruns}')

        for i in newrays:
            i.step(u_stepsize)

        state.rays = newrays
    
    if(debug_level >= DEBUG_MIN):
        et = time.time()
        dt = et-st
        nrays = len(state.rays)
        nsteps = nrays*resolution
        str0 = f'Finished tracer step ({dt:.2f}s elapsed' + (f', ~{dt/nsteps*1e6:.1f}μs/sim. step).' if nrays>0 else ').')
        print(f'{str0:<90}', state)

