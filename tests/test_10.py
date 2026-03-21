import scene
import tracer
import ray
import sensor
import matplotlib.pyplot as plt
import numpy as np
from state import State

import time

from parts_lib import LensPlanoConvex

rays = [ ray.Ray(np.array([x,0.,10.5]), np.array([0.,0.,-1.])) for x in np.linspace(-0.9,0.9,5) ]
lens0 = LensPlanoConvex(np.array([0,0,10]), np.pi, 2, 3.5, 10.0)

s = scene.Scene([lens0,])
sens = sensor.Sensor(np.array([-0.8, 0., -1.5]), np.array([0.8, 0., -1.5]))

state = State(s, rays)
ax=sens.show()
state.show(ax)
plt.gca().set_aspect('equal')
plt.show()

for i in range(150):
    tracer.trace(state, stepsize=0.1)

ax=sens.show()
state.show(ax)

plt.gca().set_aspect('equal')
plt.show()
