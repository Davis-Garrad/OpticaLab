import scene
import tracer
import ray
import colours
import matplotlib.pyplot as plt
import numpy as np
from state import State

tracer.status_update = lambda *args, **kwargs: None


def glass_index(wavelength_nm):
    '''Cauchy-style dispersive refractive index model.
    
    A and B are the Cauchy coefficients.
    
    https://en.wikipedia.org/wiki/Cauchy%27s_equation
    https://www.nature.com/articles/s41597-023-02898-2
    https://refractiveindex.info/?shelf=specs&book=SCHOTT-optical&page=N-BK7#google_vignette
    '''
    A = 1.5046
    B = 0.00420
    wavelength_um = wavelength_nm * 1e-3
    return A + B / np.square(wavelength_um)


def rms_width(xs, intensity):
    intensity = np.array(intensity)
    xs = np.array(xs)

    if(np.sum(intensity) <= 0):
        return np.inf

    avg = np.sum(xs * intensity) / np.sum(intensity)
    return np.sqrt(np.sum(intensity * np.square(xs - avg)) / np.sum(intensity))


def plane_pattern(state, z, width=4.0): ## The sensor helper was doing fine but it was yielding some odd results, basically same thing here but less corse.
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


reference_wavelength = 532.0
reference_index = glass_index(reference_wavelength)

scale = 2
focal_length = 5.0
radius = (reference_index-1) * focal_length / scale
front_profile = lambda x,y: np.sqrt(np.square(radius)-np.square(x)) - np.sqrt(np.square(radius) - 1)


def front_normal(x,y):
    diff_from_centre = np.array([x, y, front_profile(x,y)]) - np.array([0,0,-np.sqrt(np.square(radius)-1)])
    return diff_from_centre


lens = scene.SceneObject(glass_index, front_profile, np.array([0,0,10]), np.pi, scale, frontface_normal=front_normal)
s = scene.Scene([lens])

wavelengths = [450, 532, 650]
states = []

for wavelength in wavelengths:
    rays = [ray.Ray(np.array([x,0.,10.5]), np.array([0.,0.,-1.]), wavelength=wavelength) for x in np.linspace(-0.9,0.9,9)]
    state = State(s, rays)

    for i in range(80):
        tracer.trace(state, stepsize=0.1, resolution=400)

    states += [state]


fig, ax = plt.subplots(1,1)
for state in states:
    for r in state.dead_rays:
        r.show(ax=ax)
    for r in state.free_rays:
        r.show(ax=ax)
    for r in state.rays:
        r.show(ax=ax)
s.show(ax=ax)
ax.set_aspect('equal')
plt.title('Chromatic aberration ray trace')
plt.show()


z_positions = np.linspace(3.6, 4.2, 80)

plt.figure()
for wavelength,state in zip(wavelengths, states):
    widths = []
    for z in z_positions:
        xs, intensity = plane_pattern(state, z)
        widths += [ rms_width(xs, intensity) ]

    widths = np.array(widths)
    best_i = np.argmin(widths)
    best_z = z_positions[best_i]
    print(f'{wavelength}nm best focus z = {best_z:.3f}, RMS width = {widths[best_i]:.5f}')
    plt.plot(z_positions, widths, color=colours.wavelength_to_rgb(wavelength), linewidth=3, label=f'{wavelength} nm')

plt.xlabel('Measurement plane z-position')
plt.ylabel('RMS spot width')
plt.title('Chromatic aberration: focus depends on wavelength')
plt.legend()
plt.show()
