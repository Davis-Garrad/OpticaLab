import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State
 
r = ray.Ray(np.array([1.,0.,0.]), np.array([-1.,0.,-1.]))

s = scene.Scene([])

state = State(s, [r])
state.show()
plt.gca().set_aspect('equal')
plt.show()

tracer.trace(state, stepsize=3)

state.show()

plt.gca().set_aspect('equal')
plt.show()
