import scene
import numpy as np

class LensPlanoConvex(scene.SceneObject):
    def __init__(self, position, rotation, scale, index_of_refraction, focal_length):
        radius = (index_of_refraction-1)*focal_length / scale
        front_profile = lambda x,y: np.sqrt(np.square(radius)-np.square(x)) - np.sqrt(np.square(radius) - 1)
        
        def ffn(x,y):
            diff_from_centre = np.array([x,y,front_profile(x,y)]) - np.array([0,0,-np.sqrt(np.square(radius)-1)])
            return diff_from_centre# / np.sqrt(np.sum(np.square(diff_from_centre))) # doesn't need to be normalized! Will do later.

        super().__init__(index_of_refraction, front_profile, position, rotation, scale, frontfacing_normal=ffn)

