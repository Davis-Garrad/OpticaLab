import scene
import tracer
import ray
import sensor
import colours
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


def crown_index(wavelength_nm):
    wavelength_um = wavelength_nm * 1e-3
    return 1.50 + 0.004 / np.square(wavelength_um)


def flint_index(wavelength_nm): # I couldnt directly find a proper figure i could trust so made sure to have 1.60 as base, same logic as AB from before, aka a stronger base refractive index, and I also wanted 0.009 as roughly double but a but more so igher dispersion, so it should behave like flint
    wavelength_um = wavelength_nm * 1e-3
    return 1.60 + 0.009 / np.square(wavelength_um)

# + - +
lens0 = biconvex(crown_index, np.array([0,0,11.8]), 1.3, 2.5, 2.5, 0.20)
lens1 = biconcave(flint_index, np.array([0,0,10.6]), 0.85, 3.4, 3.4, 0.18)
lens2 = biconvex(crown_index, np.array([0,0,9.0]), 1.2, 2.7, 2.7, 0.20)

s = scene.Scene([lens0, lens1, lens2])
single_scene = scene.Scene([ biconvex(crown_index, np.array([0,0,10.4]), 1.35, 2.5, 2.5, 0.20) ])

wavelengths = [450, 532, 650]
states = []
single_states = []

for wavelength in wavelengths:
    rays = [ ray.Ray(np.array([x,0.,15.5]), np.array([0.,0.,-1.]), wavelength=wavelength) for x in np.linspace(-0.45,0.45,3) ]
    state = State(s, rays)
    single_state = State(single_scene, [ ray.Ray(np.array([x,0.,15.5]), np.array([0.,0.,-1.]), wavelength=wavelength) for x in np.linspace(-0.45,0.45,3) ])

    for i in range(90):
        tracer.trace(state, stepsize=0.15, resolution=100)
        tracer.trace(single_state, stepsize=0.15, resolution=100)

    states += [state]
    single_states += [single_state]


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
plt.title('Cooke triplet chromatic ray trace')
plt.show()


z_positions = np.linspace(7.4, 11.2, 28)
triplet_best_zs = []
single_best_zs = []

plt.figure()
for wavelength,state,single_state in zip(wavelengths, states, single_states):
    widths = []
    single_widths = []

    for z in z_positions:
        sens = sensor.Sensor(np.array([-3.0, 0., z]), np.array([3.0, 0., z]))
        xs, intensity = sens.get_intensity_pattern(state)
        widths += [ rms_width(xs, intensity) ]

        sens = sensor.Sensor(np.array([-3.0, 0., z]), np.array([3.0, 0., z]))
        xs, intensity = sens.get_intensity_pattern(single_state)
        single_widths += [ rms_width(xs, intensity) ]

    widths = np.array(widths)
    single_widths = np.array(single_widths)

    best_i = np.argmin(widths)
    single_best_i = np.argmin(single_widths)
    best_z = z_positions[best_i]
    single_best_z = z_positions[single_best_i]

    triplet_best_zs += [best_z]
    single_best_zs += [single_best_z]

    print(f'Cooke {wavelength}nm best focus z = {best_z:.3f}, RMS width = {widths[best_i]:.5f}')
    print(f'Single {wavelength}nm best focus z = {single_best_z:.3f}, RMS width = {single_widths[single_best_i]:.5f}')

    color = colours.wavelength_to_rgb(wavelength)
    plt.plot(z_positions, widths, linewidth=3, color=color, label=f'Cooke {wavelength} nm')
    plt.plot(z_positions, single_widths, linewidth=2, linestyle='--', color=color, label=f'Single {wavelength} nm')

triplet_best_zs = np.array(triplet_best_zs)
single_best_zs = np.array(single_best_zs)

triplet_spread = np.max(triplet_best_zs) - np.min(triplet_best_zs)
single_spread = np.max(single_best_zs) - np.min(single_best_zs)

print(f'Cooke triplet chromatic focus spread = {triplet_spread:.3f}')
print(f'Single lens chromatic focus spread = {single_spread:.3f}')

plt.xlabel('Sensor z-position')
plt.ylabel('RMS spot width')
plt.title('Cooke triplet vs single lens chromatic focus scan')
plt.legend()
plt.show()
