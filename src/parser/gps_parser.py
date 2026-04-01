import pandas as pd
from pymavlink import mavutil


def extract_gps(file_path: str) -> pd.DataFrame:
    """
    Витягує GPS-дані з бінарного лог-файлу Ardupilot.

    Поля в логу:
        TimeUS  - час з моменту старту контролера, мікросекунди
        Lat/Lng - координати в градусах (WGS-84), pymavlink вже конвертує з int*1e7
        Alt     - висота над рівнем моря, метри
        Spd     - горизонтальна швидкість від GPS, м/с
        VZ      - вертикальна швидкість, м/с (вниз = позитивне значення)
        NSats   - кількість супутників
        HDop    - горизонтальна точність (чим менше, тим краще; <2.0 = добре)
        Status  - 6 = RTK Fixed (найточніший), 3 = 3D Fix, 0 = No Fix

    Returns:
        DataFrame з колонками: timestamp, lat, lon, alt, spd, vz, n_sats, hdop, status
    """
    mav = mavutil.mavlink_connection(file_path, dialect='ardupilotmega')
    records = []

    while True:
        msg = mav.recv_match(type=['GPS'])
        if msg is None:
            break

        d = msg.to_dict()

        if d.get('I', 0) != 0:
            continue

        records.append({
            'timestamp': d['TimeUS'] / 1e6,   
            'lat':       d['Lat'],             
            'lon':       d['Lng'],             
            'alt':       d['Alt'],             
            'spd':       d['Spd'],             
            'vz':        d['VZ'],              
            'n_sats':    d['NSats'],
            'hdop':      d['HDop'],
            'status':    d['Status'],
        })

    df = pd.DataFrame(records)

    if df.empty:
        return df

    
    df = df[df['status'] >= 3].reset_index(drop=True)

    return df


def gps_sample_rate(df: pd.DataFrame) -> float:
    if len(df) < 2:
        return 0.0
    diffs = df['timestamp'].diff().dropna()
    return round(1.0 / diffs.median(), 2)