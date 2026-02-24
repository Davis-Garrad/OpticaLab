import numpy as np

def rotate(vector, angle_rad):
    return np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                     [np.sin(angle_rad),  np.cos(angle_rad)]])@vector
