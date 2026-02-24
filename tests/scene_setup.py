import scene
import matplotlib.pyplot as plt
import numpy as np

a = scene.SceneObject(1, lambda x,y: x**2+1, np.array([1, 2]), np.pi/4*0, 1)
b = scene.SceneObject(1, lambda x,y: 1-np.sqrt(np.abs(x)), np.array([-3,0]), 0, 1)

s = scene.Scene([a, b])

print(a.get_normal(0,0))
print(a.get_normal(0.5,0))
print(a.get_normal(0.75,0))
print(a.get_normal(1,0))

s.show()
plt.gca().set_aspect('equal')
plt.show()
