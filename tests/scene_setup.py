import scene
import matplotlib.pyplot as plt
import numpy as np

a = scene.SceneObject(1, lambda x,y: x**2+1, np.array([1, 2]), np.pi/4, 1)

s = scene.Scene([a])

s.show()
plt.show()
