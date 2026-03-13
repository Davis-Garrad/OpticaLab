import scene
import matplotlib.pyplot as plt
import numpy as np

r = Ray(np.array([1,0]), np.array([0,-1]))

s = scene.Scene([], [r])

print(a.get_normal(np.array([0.00,0,20]),np.array([0,0,-1])))
print(a.get_normal(np.array([0.25,0,20]),np.array([0,0,-1])))
print(a.get_normal(np.array([0.75,0,20]),np.array([0,0,-1])))
print(a.get_normal(np.array([1.00,0,20]),np.array([0,0,-1])))

s.show()
plt.gca().set_aspect('equal')
plt.show()
