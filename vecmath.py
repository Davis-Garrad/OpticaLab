import numpy as np

def rotate(vector, angle_rad):
    if(vector.shape[0] == 2):
    
        return np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                     [np.sin(angle_rad),  np.cos(angle_rad)]])@vector
    else:
        return np.array([[np.cos(angle_rad), 0, -np.sin(angle_rad)],
                         [0,0,0],
                         [np.sin(angle_rad), 0, np.cos(angle_rad)]])@vector # act on only x and z

