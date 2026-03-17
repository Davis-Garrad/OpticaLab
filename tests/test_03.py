import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State


rays = [ ray.Ray(np.array([x,0.,1.25]), np.array([0.0,0.,-1.])) for x in np.linspace(-0.9,0.9,21) ]
lens = scene.SceneObject(1.5, lambda x,y: np.sqrt(1 - x**2), np.array([0,0,1]), np.pi, 1)

s = scene.Scene([lens])

state = State(s, rays)
state.show()
plt.gca().set_aspect('equal')
plt.show()

tracer.trace(state, stepsize=3)

state.show()

plt.gca().set_aspect('equal')
plt.show()
