import scene
import tracer
import ray
import sensor
import matplotlib.pyplot as plt
import numpy as np

import time

class PlanoConvex(scene.SceneObject):
    def __init__(self, position, rotation, scale, index_of_refraction, focal_length):
        radius = (index_of_refraction-1)*focal_length / scale
        front_profile = lambda x,y: np.sqrt(np.square(radius)-np.square(x)) - np.sqrt(np.square(radius) - 1)

        super().__init__(index_of_refraction, front_profile, position, rotation, scale)


rays = [ ray.Ray(np.array([x,0.,10.5]), np.array([0.,0.,-1.])) for x in np.linspace(-0.9,0.9,5) ]
lens0 = PlanoConvex(np.array([0,0,10]), np.pi, 2, 3.5, 10.0)
lens1 = PlanoConvex(np.array([0,0,-2]), 0, 1, 3.5, 2.0)

s = scene.Scene([lens0,lens1])
sens = sensor.Sensor(np.array([-0.8, 0., -1.5]), np.array([0.8, 0., -1.5]))

state = tracer.State(s, rays)
ax=sens.show()
state.show(ax)
plt.gca().set_aspect('equal')
plt.show()

for i in range(100):
    #print(f'{i}/100')
    tracer.trace(state, stepsize=0.1)

ax=sens.show()
state.show(ax)

plt.gca().set_aspect('equal')
plt.show()
