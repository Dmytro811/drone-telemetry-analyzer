import numpy as np
from pyproj import Transformer

def convert_to_enu(df):
    """
    Convert WGS-84 coordinates to ENU (East, North, Up) relative to the first point.

    Args:
        df (pd.DataFrame): DataFrame with columns 'lat', 'lon', 'alt'

    Returns:
        pd.DataFrame: DataFrame with additional columns 'east', 'north', 'up'
    """
    if df.empty:
        return df

    # Reference point (first point)
    lat0 = df['lat'].iloc[0]
    lon0 = df['lon'].iloc[0]
    alt0 = df['alt'].iloc[0]

    # Transformer from WGS84 to ENU
    transformer = Transformer.from_crs("EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs", always_xy=True)

    east, north = transformer.transform(df['lon'], df['lat'])
    up = df['alt'] - alt0

    df = df.copy()
    df['east'] = east - east.min()  # Center the coordinates
    df['north'] = north - north.min()
    df['up'] = up - up.min()

    return df