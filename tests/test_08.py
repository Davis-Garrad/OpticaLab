import scene
import tracer
import ray
import sensor
import matplotlib.pyplot as plt
import numpy as np

import time

rays = [ ray.Ray(np.array([x,0.,1.5]), np.array([0.,0.,-1.])) for x in np.linspace(-0.9,0.9,21) ]
lens = scene.SceneObject(3.5, lambda x,y: 0.9-np.square(x)*0.1, np.array([0,0,0]), np.pi * (1-0.01), 1)

s = scene.Scene([lens])
sens = sensor.Sensor(np.array([0.05, 0., -1.5]), np.array([-0.5, 0., -1.5]))

state = tracer.State(s, rays)
ax=state.show()
sens.show(ax)
plt.gca().set_aspect('equal')
plt.show()

for i in range(3):
    tracer.trace(state, stepsize=1)

ax=state.show()
sens.show(ax)
print(sens.intensity(state))


plt.gca().set_aspect('equal')
plt.show()
