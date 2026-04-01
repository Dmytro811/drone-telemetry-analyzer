import pandas as pd
import numpy as np


def parse_log(file_path: str) -> pd.DataFrame:
    """
    MOCK parser for development.
    Generates fake flight data.
    """

    n = 500  
    dt = 0.1  

    t = np.arange(0, n * dt, dt)

   
    lat0, lon0 = 49.0, 24.0

    lat = lat0 + 0.0001 * np.sin(t / 10)
    lon = lon0 + 0.0001 * np.cos(t / 10)
    alt = 300 + 20 * np.sin(t / 20)

    acc_x = 0.5 * np.sin(t)
    acc_y = 0.3 * np.cos(t)
    acc_z = 9.8 + 0.1 * np.sin(t / 5)

    df = pd.DataFrame({
        "timestamp": t,
        "lat": lat,
        "lon": lon,
        "alt": alt,
        "acc_x": acc_x,
        "acc_y": acc_y,
        "acc_z": acc_z,
    })

    return df