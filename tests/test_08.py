import scene
import tracer
import ray
import sensor
import matplotlib.pyplot as plt
import numpy as np
from state import State


import time

rays = [ ray.Ray(np.array([x,0.,1.5]), np.array([0.,0.,-1.])) for x in np.linspace(-0.9,0.9,50) ]
lens = scene.SceneObject(3.5, lambda x,y: 0.9-np.square(x)*0.1, np.array([0,0,0]), np.pi, 1)

s = scene.Scene([lens])
sens = sensor.Sensor(np.array([-0.8, 0., -1.5]), np.array([0.8, 0., -1.5]))

state = State(s, rays)
ax=sens.show()
state.show(ax)
plt.gca().set_aspect('equal')
plt.show()

for i in range(30):
    print(f'{i}/30')
    tracer.trace(state, stepsize=0.25)

ax=sens.show()
state.show(ax)

plt.gca().set_aspect('equal')
plt.show()

dmax = 3
for i in np.linspace(0, dmax, 30):
    sens.pos0[-1] = -1.5-i
    sens.pos1[-1] = -1.5-i
    plt.plot(*sens.get_intensity_pattern(state), alpha=0.5, color=(i/dmax, 1-i/dmax, i/dmax))
    plt.suptitle('Green=close to lens, magenta=far from lens')
    plt.xlabel('Translation off x-axis')
    plt.ylabel('Intensity')
    print(f'                        \rPlotting: {i/dmax*100:.2f}%', end='')
plt.show()
