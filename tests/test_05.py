import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State


import time

rays = [ ray.Ray(np.array([x,0.,1.25]), np.array([0.25,0.,-1.])) for x in np.linspace(-0.3,0.3,5) ]
lens = scene.SceneObject(np.inf, lambda x,y: np.ones_like(x)*0.1, np.array([0,0,0]), 0, 1)

s = scene.Scene([lens])

state = State(s, rays)
state.show()
plt.gca().set_aspect('equal')
plt.show()

tracer.trace(state, stepsize=3)

state.show()

plt.gca().set_aspect('equal')
plt.show()
