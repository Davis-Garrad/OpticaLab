import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np

r = ray.Ray(np.array([1.,0.,0.]), np.array([-1.,0.,-1.]))

s = scene.Scene([])

state = tracer.State(s, [r])
state.show()
plt.gca().set_aspect('equal')
plt.show()

for i in range(10):
    tracer.trace(state)

state.show()

plt.gca().set_aspect('equal')
plt.show()
