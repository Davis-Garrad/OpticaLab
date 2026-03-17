import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State


rays = [ ray.Ray(np.array([x,0.,1.25]), np.array([0.5,0.,-1.])) for x in np.linspace(-0.9,-0.5,4) ]
lens = scene.SceneObject(2.5, lambda x,y: 1 * np.ones_like(x), np.array([-1,0,0]), -np.pi/8, 0.8)

s = scene.Scene([lens])

state = State(s, rays)
state.show()
plt.gca().set_aspect('equal')
plt.show()

tracer.trace(state, stepsize=3)

state.show()

plt.gca().set_aspect('equal')
plt.show()
