import numpy as np
import pandas as pd

def convert_to_enu(df_gps):
    """
    Перетворює глобальні координати (Lat, Lon, Alt) у локальні метри (East, North, Up).
    Виправлено: висота тепер рахується від 0 (точки зльоту).
    """
    if df_gps is None or df_gps.empty:
        return pd.DataFrame()

    # 1. Очищення даних від порожніх значень (щоб не зламати математику)
    df = df_gps.copy().dropna(subset=['lat', 'lon', 'alt'])
    
    if len(df) < 2:
        return pd.DataFrame()

    # 2. Визначаємо референсну точку (центр координат [0,0,0])
    lat0 = np.radians(df['lat'].iloc[0])
    lon0 = np.radians(df['lon'].iloc[0])
    alt0 = df['alt'].iloc[0]

    # Константи еліпсоїда WGS84
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 2 * f - f**2

    def to_ecef(lat_deg, lon_deg, alt_val):
        lat_rad = np.radians(lat_deg)
        lon_rad = np.radians(lon_deg)
        N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)
        x = (N + alt_val) * np.cos(lat_rad) * np.cos(lon_rad)
        y = (N + alt_val) * np.cos(lat_rad) * np.sin(lon_rad)
        z = (N * (1 - e2) + alt_val) * np.sin(lat_rad)
        return x, y, z

    # 3. Конвертація всіх точок у систему ECEF
    x, y, z = to_ecef(df['lat'].values, df['lon'].values, df['alt'].values)
    x0, y0, z0 = to_ecef(df['lat'].iloc[0], df['lon'].iloc[0], alt0)

    dx, dy, dz = x - x0, y - y0, z - z0

    # 4. Перехід у систему ENU (East, North, Up) через матрицю повороту
    e = -np.sin(lon0) * dx + np.cos(lon0) * dy
    n = -np.sin(lat0)*np.cos(lon0)*dx - np.sin(lat0)*np.sin(lon0)*dy + np.cos(lat0)*dz
    u = np.cos(lat0)*np.cos(lon0)*dx + np.cos(lat0)*np.sin(lon0)*dy + np.sin(lat0)*dz

    # 5. ВАЖЛИВИЙ ФІКС: Робимо вертикальну вісь відносно старту
    # Без цього графік буде "плавати" на висоті 500+ метрів і здаватися пласким
    u_relative = u - u[0]

    # Формуємо фінальний DataFrame
    return pd.DataFrame({
        'east': e,
        'north': n,
        'up': u_relative,
        'spd': df['spd'] if 'spd' in df else 0,
        'timestamp': df['timestamp']
    })