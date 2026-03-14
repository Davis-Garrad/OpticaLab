import numpy as np
import matplotlib.pyplot as plt

import vecmath

import dguid
import cfgs
from defines import *
 
# constants

dl = float(cfgs.sargs['dl']) # This defines the scale that normal approximation calculations will use.
object_resolution = int(cfgs.sargs['object_resolution']) # num evaluation points for object preprocessing and display. Jankier objects need higher resolution, smooth objects don't.
debug_level = int(cfgs.sargs['debug_level'])

# definitions

def approximate_normal(surface_function, x, y, dL=dl):
    '''Finds the approximate front-facing (positive-z) surface normal of the surface given by surface function, a function taking some x and y values and spitting out a z value. Basically just very simple gradient function, so please make sure that surface_function is smooth compared to dL.'''
    # designate some corners of the domain to approximate the normal at the centre of
    x1 = x-dL/2
    x2 = x+dL/2
    y1 = y-dL/2
    y2 = y+dL/2

    # evaluate at the corners of the square (domain) we're approximating the normal of
    o = surface_function(x1, y1)
    u = surface_function(x2, y1)
    v = surface_function(x1, y2)

    # now, we have two orthogonal vectors ("height" changes) giving us df/dx (du) and df/dy (dv)
    du = (u - o) # associated with dx
    dv = (v - o) # associated with dy

    # it's cross product time
    # x (cross) y = z, so we need to calculate df/dx (cross) df/dy to find the upward facing normal
    # This is just (dx, 0, du) (cross) (0, dy, dv) = (-du*dy, -dx*dv, dx*dy)

    # if we wanted the other normal (backfacing), we can just negatize the whole thing.... Since cross products just _work_ like that. Cool.

    normal = np.array([-du*dL, -dL*dv, dL*dL])

    # and normalise the normal... because it wasn't normal enough already!
    normal /= np.sqrt(np.sum(np.square(normal)))

    return normal

class SceneObjectType:
    '''A 3D shape with optical properties, basically. Provides some nice geometric functionality.'''
    def __init__(self, index_of_refraction_x, frontface, index_of_refraction_y=1, backface=lambda x,y: np.zeros_like(x), **kwargs):
        '''Defines a 3D object with front face height profile frontface: a function with x and y dependence. Similar for back face. These are both defined with resppect to the same origin, the placement position of the object in the scene. Can be birefringent. Assumed that x and y vary between -1 and 1, and the profiles will be scaled as appropriate for larger objects.'''
        self.index_x = index_of_refraction_x
        self.index_y = index_of_refraction_x
        if(self.index_x != self.index_y):
            raise NotImplemented("Birefringence is not implemented in Fresnel equations, nor in the tracer.")
        self.frontface = frontface
        self.backface = backface

        if('id' in kwargs.keys()):
            self.id = kwargs['id']
        else:
            self.id = dguid.get_uuid()
        if(debug_level >= DEBUG_MIN):
            print(f'Creating optical component {self.id}')

        if('frontface_normal' in kwargs.keys()):
            self.get_normal = kwargs['frontface_normal']
        if('backface_normal' in kwargs.keys()):
            self.get_backfacing_normal = kwargs['backface_normal']

        
        fronteval = frontface(np.linspace(-1,1,object_resolution)[:,None], np.linspace(-1,1,object_resolution)[None,:])
        backeval = backface(np.linspace(-1,1,object_resolution)[:,None], np.linspace(-1,1,object_resolution)[None,:])

        self.min_width = np.min(fronteval - backeval)
        self.boundingbox = np.array([-1, np.min(backeval), 1, np.max(fronteval)]) # width in -x,-y,x,y from position

    def get_normal(self, x, y, back=False):
        '''Gets one of the normals. Points in the forward (+z) direction. This is an approximation. If you know the exact relation, please provide it as a kwarg to init.'''
        if(debug_level >= DEBUG_SOME):
            print(f'Approximating{' backfacing' if back else ''} normal for component {self.id} (local pos {x:.3f},{y:.3f})')
        normal = approximate_normal(self.backface if back else self.frontface, x, y)
        return normal

    def get_outline(self):
        '''Creates a polygon for display purposes (x and z coordinates)'''
        xs = np.linspace(-1, 1, object_resolution)
        front = self.frontface(xs, 0)
        back = self.backface(xs, 0)

        # I can't just call everything xs.....
        X_ARR = np.append(np.append(xs, xs[-1::-1]), xs[0])
        Z_ARR = np.append(np.append(front, back[-1::-1]), front[0])

        return X_ARR, Z_ARR

class SceneObject(SceneObjectType):
    '''A physical object in 3D space, with some transformations.'''
    def __init__(self, index_x, frontface, position, rotation, scale, *args, **kwargs):
        '''Rotation is around the object's origin, in radians'''
        super().__init__(index_x, frontface, *args, **kwargs)
        self.scale = scale
        self.pos = position
        self.rot = rotation

    def show(self, ax=None):
        if(ax is None):
            ax = plt

        x,z=super().get_outline()

        x *= self.scale
        z *= self.scale

        newvec = vecmath.rotate(np.array([x, z]), self.rot)

        x = newvec[0] + self.pos[0]
        z = newvec[1] + self.pos[-1] # there might be a y coordinate in index 1

        ax.plot(x, z)

        # bounding circle
        theta = np.linspace(0, 2*np.pi, 360)
        c,r=self.get_boundingcircle()
        ax.plot(c[0]+np.cos(theta)*r, c[-1]+np.sin(theta)*r, linestyle='--', color='k')

    def get_boundingbox(self):
        '''Gets a (necessarily larger or identical) bounding box that has been transformed as the object has. There's a bit of geometry here.'''
        bl=self.boundingbox[:2] # -x,-y corner
        br=np.array([self.boundingbox[2],self.boundingbox[1]]) # +x,-y corner
        tr=self.boundingbox[2:] # +x,+y corner
        tl=np.array([self.boundingbox[0],self.boundingbox[3]]) # -x,+y corner

        newbl = vecmath.rotate(bl, self.rot) # rotate the corners
        newbr = vecmath.rotate(br, self.rot)
        newtl = vecmath.rotate(tl, self.rot)
        newtr = vecmath.rotate(tr, self.rot)
        
        composite = np.concatenate((newbl, newbr, newtl, newtr))

        xs = composite[0::2]
        zs = composite[1::2]

        neg = np.array([np.min(xs), np.min(zs)])
        pos = np.array([np.max(xs), np.max(zs)])

        neg *= self.scale
        neg += np.array([self.pos[0], self.pos[-1]]) # y translations are not supported.
        pos *= self.scale
        pos += np.array([self.pos[0], self.pos[-1]])

        return np.append(neg, pos) # create the new bounding box and return

    def get_boundingcircle(self):
        '''Returns (centreposition, max_radius)'''

        bb = self.get_boundingbox()
        avg_x = np.average(bb[0::2])
        avg_z = np.average(bb[1::2])
        centre = np.array([avg_x, avg_z])
        radius_neg = np.sqrt(np.sum(np.square(centre-bb[:2])))
        radius_pos = np.sqrt(np.sum(np.square(centre-bb[2:])))

        true_centre = np.array([avg_x, 0, avg_z])


        return (true_centre, np.maximum(radius_neg, radius_pos))

    def is_inside(self, r):
        '''Checks if a worldspace position `r` is inside the geometry. A bit of an expensive calulation'''
        relative_to_obj = r-self.pos

        relative_to_obj = vecmath.rotate(relative_to_obj, -self.rot) # "un"-rotate x, z around y
        relative_to_obj /= self.scale

        top = self.frontface(*relative_to_obj[:2])
        bottom = self.backface(*relative_to_obj[:2])

        isinside = (bottom <= relative_to_obj[-1] <= top) and (-1 <= relative_to_obj[0] <= 1)
        return isinside

    def get_normal(self, r, prop_direction):
        '''Gets the appropriate normal vector at some real-world position r (x,y,z) and propagation direction prop_direction'''
        # undo the translations this object has undergone
        relative_to_obj = r-self.pos

        newvec = vecmath.rotate(np.array([relative_to_obj[0], relative_to_obj[-1]]), -self.rot) # "un"-rotate x, z around y
        new_prop = vecmath.rotate(np.array([prop_direction[0], prop_direction[-1]]), -self.rot)

        relative_to_obj[0] = newvec[0]
        relative_to_obj[-1] = newvec[-1]
        relative_to_obj /= self.scale

        # now, x (or x,y) is/are between -1 and 1. We actually also have the z component, so we can decide if we're in front of this thing, inside of it, or behind it.
        x,y,z = relative_to_obj
        # errors will occur if I've done something wrong with shapes. No x,y,z will be defined.

        top = self.frontface(x,y)
        bottom = self.backface(x,y)
        normal=None
        if(z > top): # in front of
            if(new_prop[-1] > 0):
                # in front of, but was likely inside. Flip to the inside
                normal = -super().get_normal(x, y, False)
            else:
                # in front of, and was outside previously.
                normal = super().get_normal(x, y, False)
        elif(top >= z >= bottom): # inside
            if(new_prop[-1] > 0):
                # inside, and moving to the top. Front normal, and flip to the inside
                normal = -super().get_normal(x, y, False)
            else:
                # inside, and moving to the bottom. Back normal
                normal = super().get_normal(x, y, True)
        else: # behind
            if(new_prop[-1] > 0):
                # behind, and moving into. back normal & flip to outside
                normal = -super().get_normal(x, y, True)
            else:
                # behind, and was likely inside previously. take back
                normal = super().get_normal(x, y, True)

        return vecmath.rotate(normal, self.rot)

class Scene:
    '''Just a collection of objects with what are essentially helper functions'''
    def __init__(self, objects=[]):
        self.objects = objects

    def check_intersecting(self, position):
        '''Finds the object that the position lies inside of. This is assuming that there can only be zero or one object at any point (i.e., objects cannot intersect with each other). If there is more than one object, this will return the first for efficiency. It is the onus of the programmer to avoid such problems. Returns None if there is not an intersection.'''

        # get everything which intersects the bounding boxes
        possible_intersects = []
        for i in self.objects:
            bb = i.get_boundingbox()
            if(bb[2] >= position[0] >= bb[0] and
               bb[3] >= position[-1] >= bb[1]):
                # inside the box! Add it to the list
                possible_intersects += [i]
        
        # do the expensive calculations - is the point actually inside the object?
        for i in possible_intersects:
            if(i.is_inside(position)): # I end up calculating this multiple times, but the readability cost is too high to setup a cache and stuff. I'd rather take the constant time hit.
                return i

        return None

    def get_nextinterface(self, position, direction):
        '''Returns the position of and squared distance to the next object that a given ray will intersect with, given a direction and origin. Returns None,None if there are no objects, or None,0 if we're already inside any of the objects' bounding spheres.'''
        perp    = np.array([direction[2], direction[1], -direction[0]]) # sign won't matter, we care about relative differences later...
        in_path = []
        #TODO: vectorize this?
        for i in range(len(self.objects)):
            centre,rad = self.objects[i].get_boundingcircle()
            c = centre-position
            # need that the two sides of the bounding circle lie on different sides of the propagation (direction) vector
            # some basic vector algebra+geometry shows that this is equivalent to centre(dot)perp_to_propagation \elem (-r,r)
            perp_proj = np.dot(perp, c)
            if(np.abs(perp_proj) <= rad): # in the path
                in_path += [(i,c,rad)] # pass on to next step

        if(in_path == []):
            return None,None
        min_dist = -1
        min_dist_i = None
        for (i,c_rel,rad) in in_path: # so many `in`'s
            dist_sqrd = np.sum(np.square(c_rel))
            rad_sqrd = np.square(rad)
            if(dist_sqrd <= rad_sqrd): # there's a possibility we're in this object, in front of it, or have yet to hit it! Quit, and let the raytracer do its job!
                return None,0
            prop_proj = np.dot(direction, c_rel) # to figure out if it's in front or behind us
            if(prop_proj > 0): # in front
                if(dist_sqrd-rad_sqrd < min_dist or min_dist==-1): # the front of the bounding sphere is close! Record it
                    min_dist = dist_sqrd-rad_sqrd
                    min_dist_i = i
        if(min_dist is -1): # didn't find anything in front of us!
            return None,None

        closest_point = c_rel - c_rel/np.sqrt(np.sum(np.square(c_rel))) * rad + position

        return closest_point,min_dist

    
    def show(self, ax=None):
        for i in self.objects:
            i.show(ax)
