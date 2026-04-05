import numpy as np

def Haversine(lats, lons):
    R = 6371000.0  
    phi1, phi2 = np.radians(lats[:-1]), np.radians(lats[1:])
    lambda1, lambda2 = np.radians(lons[:-1]), np.radians(lons[1:])
    delta_phi = phi2 - phi1
    delta_lambda = lambda2 - lambda1
    a = np.sin(delta_phi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distances = R * c
    return np.sum(distances)