import numpy as np
import matplotlib.pyplot as plt

import vecmath

import dguid

# constants

dl = 1e-3 # This defines the scale that normal approximation calculations will use.

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

        self.min_width = np.min(frontface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]) - backface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]))

    def get_normal(self, x, y):
        '''Gets the front face normal. Points in the forward direction. This is an approximation. If you know the exact relation, please provide it as a kwarg to init.'''
        print(f'Approximating normal for component {self.id}')
        return approximate_normal(self.frontface, x, y)

    def get_backfacing_normal(self, x, y):
        '''Gets the back face normal. Points in the backward direction.'''
        print(f'Approximating backfacing normal for component {self.id}')
        return -approximate_normal(self.backface, x, y)

    def get_outline(self):
        '''Creates a polygon for display purposes (x and z coordinates)'''
        xs = np.linspace(-1, 1, 100)
        front = self.frontface(xs, 0)
        back = self.backface(xs, 0)

        X_ARR = np.append(np.append(xs, xs[-1:0:-1]), xs[0])
        Z_ARR = np.append(np.append(front, back[-1:0:-1]), front[0])

        return X_ARR, Z_ARR

class SceneObject(SceneObjectType):
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

class Scene:
    def __init__(self, objects=[], tracingscale=None):
        '''`tracingscale` defines the base step size (which can later be further scaled down, but it's best to set it here properly). If None, this will be set to 1/100 the smallest optical element.'''
        self.objects = objects

        if(tracingscale is None):
            min_width = 1
            for i in self.objects:
                min_width = np.minimum(i.min_width*i.scale, min_width)
    
    def show(self, ax=None):
        for i in self.objects:
            i.show(ax)
