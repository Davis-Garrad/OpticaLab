import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State


import time

rays = [ ray.Ray(np.array([x,0.,1.5]), np.array([0.,0.,-1.])) for x in np.linspace(-0.9,0.9,21) ]
lens = scene.SceneObject(3.5, lambda x,y: 0.9-np.square(x)*0.1, np.array([0,0,0]), np.pi * (1-0.01), 1)

s = scene.Scene([lens])

state = State(s, rays)
state.show()
plt.gca().set_aspect('equal')
plt.show()

for n in range(6):
    tracer.trace(state, stepsize=1)

state.show()

plt.gca().set_aspect('equal')
plt.show()
