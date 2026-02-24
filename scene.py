import numpy as np
import matplotlib.pyplot as plt

class SceneObjectType:
    def __init__(self, index_of_refraction_x, frontface, index_of_refraction_y=1, backface=lambda x,y: np.zeros_like(x)):
        '''Defines a 3D object with front face height profile frontface: a function with x and y dependence. Similar for back face. These are both defined with resppect to the same origin, the placement position of the object in the scene. Can be birefringent. Assumed that x and y vary between -1 and 1, and the profiles will be scaled as appropriate for larger objects.'''
        self.index_x = index_of_refraction_x
        self.index_y = index_of_refraction_y
        self.frontface = frontface
        self.backface = backface

        self.min_width = np.min(frontface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]) - backface(np.linspace(-1,1,100)[:,None], np.linspace(-1,1,100)[None,:]))

    def get_normal(self, x, y):
        '''Gets the front face normal. Points in the forward direction.'''

    def get_backfacing_normal(self, x, y):
        '''Gets the back face normal. Points in the backward direction.'''

    def show(self, ax=None):
        '''Shows the polygon'''
        xs = np.linspace(-1, 1, 100)
        front = self.frontface(xs, 0)
        back = self.backface(xs, 0)

        if(ax is None):
            ax = plt
        ax.plot(np.append(xs, xs[-1:0:-1]), np.append(front, back[-1:0:-1]))


class SceneObject(SceneObjectType):
    def __init__(self, index_x, frontface, scale, *args, **kwargs):
        super().__init__(index_x, frontface, *args, **kwargs)
        self.scale = scale

class Scene:
    def __init__(self, objects=[], tracingscale=None):
        '''`tracingscale` defines the base step size (which can later be further scaled down, but it's best to set it here properly). If None, this will be set to 1/100 the smallest optical element.'''
        self.objects = objects

        if(tracingscale is None):
            min_width = 1
            for i in self.objects:
                min_width = np.minimum(self.objects[i].min_width*self.objects[i].scale, min_width)
    
    def show(self, ax=None):
        for i in self.objects:
            self.objects.show(ax)
