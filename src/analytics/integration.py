import numpy as np

def trapezoidal_integration(times, accelerations, initial_velocity=0.0):
    dt = np.diff(times)
    avg_accel = (accelerations[:-1] + accelerations[1:]) / 2.0
    dv = avg_accel * dt
    velocities = np.concatenate(([initial_velocity], initial_velocity + np.cumsum(dv)))
    return velocities