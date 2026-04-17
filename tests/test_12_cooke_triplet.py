import scene
import tracer
import ray
import matplotlib.pyplot as plt
import numpy as np
from state import State

tracer.max_depth = 6 # pls increase if you got a better pc
tracer.status_update = lambda *args, **kwargs: None


def rms_width(xs, intensity):
    intensity = np.array(intensity)
    xs = np.array(xs)

    if(np.sum(intensity) <= 0):
        return np.inf

    avg = np.sum(xs * intensity) / np.sum(intensity)
    return np.sqrt(np.sum(intensity * np.square(xs - avg)) / np.sum(intensity))


def plane_pattern(state, z, width=10.0):
    xs = []
    intensity = []

    for r in state.rays + state.free_rays + state.dead_rays:
        z0 = r.origin[-1]
        z1 = r.pos[-1]
        if(z0 == z1):
            continue
        if(not(min(z0, z1) <= z <= max(z0, z1))):
            continue

        t = (z - z0)/(z1 - z0)
        x = r.origin[0] + t*(r.pos[0] - r.origin[0])
        if(np.abs(x) <= width):
            xs += [x]
            intensity += [r.intensity]

    if(len(xs) == 0):
        return [0], [0]

    return xs, intensity


def sag(radius, x):
    return np.sqrt(np.square(radius) - np.square(x)) - np.sqrt(np.square(radius) - 1)


def biconvex(index, position, scale, radius_front, radius_back, thickness):
    frontface = lambda x,y: thickness/2 + sag(radius_front, x)
    backface = lambda x,y: -thickness/2 - sag(radius_back, x)
    return scene.SceneObject(index, frontface, position, np.pi, scale, backface=backface)


def biconcave(index, position, scale, radius_front, radius_back, thickness):
    frontface = lambda x,y: thickness/2 - sag(radius_front, x)
    backface = lambda x,y: -thickness/2 + sag(radius_back, x)
    return scene.SceneObject(index, frontface, position, np.pi, scale, backface=backface)


# Cooke triplet style layout:
# + - +
lens0 = biconvex(1.52, np.array([0,0,11.8]), 1.3, 2.5, 2.5, 0.20) # crown https://en.wikipedia.org/wiki/Crown_glass_(optics)
lens1 = biconcave(1.62, np.array([0,0,10.6]), 0.85, 3.4, 3.4, 0.18) # flint https://en.wikipedia.org/wiki/Flint_glass
lens2 = biconvex(1.52, np.array([0,0,9.0]), 1.2, 2.7, 2.7, 0.20) # same https://en.wikipedia.org/wiki/Crown_glass_(optics)

s = scene.Scene([lens0, lens1, lens2])

single_scene = scene.Scene([ biconvex(1.52, np.array([0,0,12.63]), 1.4, 3.1, 3.1, 0.20) ])

rays = [ ray.Ray(np.array([x,0.,15.5]), np.array([0.,0.,-1.]), wavelength=532) for x in np.linspace(-0.7,0.7,7) ]
state = State(s, rays)
single_state = State(single_scene, [ ray.Ray(np.array([x,0.,15.5]), np.array([0.,0.,-1.]), wavelength=532) for x in np.linspace(-0.7,0.7,7) ])

for i in range(150):
    tracer.trace(state, stepsize=0.15, resolution=180)
    tracer.trace(single_state, stepsize=0.15, resolution=180)


fig, ax = plt.subplots(1,1)
state.show(ax=ax)
ax.set_aspect('equal')
plt.title('Cooke triplet ray trace')
plt.show()


z_positions = np.linspace(6.5, 10.5, 80)
widths = []
single_widths = []
for z in z_positions:
    xs, intensity = plane_pattern(state, z)
    widths += [rms_width(xs, intensity) ]
    xs, intensity = plane_pattern(single_state, z)
    single_widths += [ rms_width(xs, intensity) ]

widths = np.array(widths)
single_widths = np.array(single_widths)
best_i = np.argmin(widths)
best_z = z_positions[best_i]
single_best_i = np.argmin(single_widths)
single_best_z = z_positions[single_best_i]
print(f'Cooke triplet best focus z = {best_z:.3f}, RMS width = {widths[best_i]:.5f}')
print(f'Single lens best focus z = {single_best_z:.3f}, RMS width = {single_widths[single_best_i]:.5f}')

plt.figure()
plt.plot(z_positions, widths, linewidth=3, color='darkgreen')
plt.plot(z_positions, single_widths, linewidth=3, color='darkorange')
plt.xlabel('Measurement plane z-position')
plt.ylabel('RMS spot width')
plt.title('Cooke triplet vs single lens focus scan')
plt.legend(['Cooke triplet', 'Single lens'])
plt.show()
