import numpy as np
import matplotlib.pyplot as plt

import vecmath

class SceneObjectType:
    def __init__(self, index_of_refraction_x, frontface, index_of_refraction_y=1, backface=lambda x,y: np.zeros_like(x), **kwargs):
        '''Defines a 3D object with front face height profile frontface: a function with x and y dependence. Similar for back face. These are both defined with resppect to the same origin, the placement position of the object in the scene. Can be birefringent. Assumed that x and y vary between -1 and 1, and the profiles will be scaled as appropriate for larger objects.'''
        self.index_x = index_of_refraction_x
        self.index_y = index_of_refraction_y
        self.frontface = frontface
        self.backface = backface

        if('frontface_normal' in kwargs):
            #TODO do these options, and implement a numerical normal calculator

        self.min_width = np.min(frontface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]) - backface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]))

    def get_normal(self, x, y):
        '''Gets the front face normal. Points in the forward direction.'''

    def get_backfacing_normal(self, x, y):
        '''Gets the back face normal. Points in the backward direction.'''

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
