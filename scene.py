import numpy as np
import matplotlib.pyplot as plt

import vecmath

import dguid
import cfgs

# constants

dl = float(cfgs.sargs['dl']) # This defines the scale that normal approximation calculations will use.
object_resolution = int(cfgs.sargs['object_resolution']) # num evaluation points for object preprocessing and display. Jankier objects need higher resolution, smooth objects don't.

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
        self.index_y = index_of_refraction_y
        self.frontface = frontface
        self.backface = backface

        if('id' in kwargs.keys()):
            self.id = kwargs['id']
        else:
            self.id = dguid.get_uuid()
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
        '''Gets the front face normal. Points in the forward direction. This is an approximation. If you know the exact relation, please provide it as a kwarg to init.'''
        print(f'Approximating{' backfacing' if back else ''} normal for component {self.id}')
        return approximate_normal(self.backface if back else self.frontface, x, y) * (-1 if back else 1)

    def get_outline(self):
        '''Creates a polygon for display purposes (x and z coordinates)'''
        xs = np.linspace(-1, 1, object_resolution)
        front = self.frontface(xs, 0)
        back = self.backface(xs, 0)

        # I can't just call everything xs.....
        X_ARR = np.append(np.append(xs, xs[-1:0:-1]), xs[0])
        Z_ARR = np.append(np.append(front, back[-1:0:-1]), front[0])

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

    def get_boundingbox(self):
        '''Gets a (necessarily larger or identical) bounding box that has been transformed as the object has. There's a bit of geometry here.'''
        neg=self.boundingbox[:2] # -x,-y corner
        pos=self.boundingbox[2:] # +x,+y corner

        newneg = vecmath.rotate(neg, self.rot) # rotate the corners
        newpos = vecmath.rotate(pos, self.rot)

        neg = np.maximum(newneg, neg) # the bounding box needs to be largest rectangular area which encloses the object. Thanks.
        pos = np.maximum(newpos, pos)

        neg *= scale
        neg += np.array([self.pos[0], self.pos[-1]]) # y translations are not supported.
        pos *= scale
        pos += np.array([self.pos[0], self.pos[-1]])

        return np.append(neg, pos) # create the new bounding box and return

    def get_normal(self, r, prop_direction):
        '''Gets the appropriate normal vector at some real-world position r (can be x,z or x,y,z. Both work.) and propagation direction prop_direction'''
        # undo the translations this object has undergone
        relative_to_obj = r-self.pos

        newvec = vecmath.rotate(np.array([relative_to_obj[0], relative_to_obj[-1]]), -self.rot) # "un"-rotate x, z around y
        new_prop = vecmath.rotate(np.array([prop_direction[0], prop_direction[-1]]), -self.rot)

        relative_to_obj[0] = newvec[0]
        relative_to_obj[-1] = newvec[-1]
        relative_to_obj /= self.scale

        # now, x (or x,y) is/are between -1 and 1. We actually also have the z component, so we can decide if we're in front of this thing, inside of it, or behind it.
        print(relative_to_obj)
        x,y,z = relative_to_obj
        # errors will occur if I've done something wrong with shapes. No x,y,z will be defined.

        top = self.frontface(x,y)
        bottom = self.backface(x,y)
        if(z > top): # in front of
            if(new_prop[-1] > 0):
                # in front of, but was likely inside. Flip to the inside
                return -super().get_normal(x, y, False)
            else:
                # in front of, and was outside previously.
                return super().get_normal(x, y, False)
        elif(z <= top and z >= bottom): # inside
            if(new_prop[-1] > 0):
                # inside, and moving to the top. Front normal, and flip to the inside
                return super().get_normal(x, y, False)
            else:
                # inside, and moving to the bottom. Back normal and flip to inside
                return -super().get_normal(x, y, True)
        else: # behind
            if(new_prop[-1] > 0):
                # behind, and moving into. back normal
                return super().get_normal(x, y, True)
            else:
                # behind, and was likely inside previously. flip back normal
                return -super().get_normal(x, y, True)

class Scene:
    '''Just a collection of objects with what are essentially helper functions'''
    def __init__(self, objects=[]):
        self.objects = objects

    def check_intersecting(self, position):
        '''Finds all objects which the position lies in the bounding box of. Returns a list of objects, or an empty list if no objects are found'''
        possible_intersects = []
        for i in self.objects:
            bb = i.get_boundingbox(position)
            if(np.all(position[:2] >= bb[:2]) and np.all(position[2:] <= bb[2:])):
                # inside the box! Add it to the list
                possible_intersects += [i]
        return possible_intersects
    
    def show(self, ax=None):
        for i in self.objects:
            i.show(ax)
