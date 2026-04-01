import pandas as pd
from pymavlink import mavutil


def extract_imu(file_path: str, instance: int = 0) -> pd.DataFrame:
    """
    Витягує IMU-дані з бінарного лог-файлу Ardupilot.

    Поля в логу:
        TimeUS      - час, мікросекунди
        AccX/Y/Z    - лінійне прискорення по осях тіла дрона, м/с²
                      AccZ в спокої ≈ -9.8 (сила тяжіння, вісь Z вниз у NED)
        GyrX/Y/Z    - кутова швидкість (гіроскоп), рад/с
        T           - температура IMU, °C (для температурної компенсації)
        AHz         - реальна частота акселерометра, Гц
        GHz         - реальна частота гіроскопа, Гц

    Returns:
        DataFrame з колонками: timestamp, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, temp, sample_hz
    """
    mav = mavutil.mavlink_connection(file_path, dialect='ardupilotmega')
    records = []

    while True:
        msg = mav.recv_match(type=['IMU'])
        if msg is None:
            break

        d = msg.to_dict()

       
        if d.get('I', 0) != instance:
            continue

        records.append({
            'timestamp': d['TimeUS'] / 1e6,   
            'acc_x':     d['AccX'],            
            'acc_y':     d['AccY'],            
            'acc_z':     d['AccZ'],            
            'gyr_x':     d['GyrX'],           
            'gyr_y':     d['GyrY'],            
            'gyr_z':     d['GyrZ'],            
            'temp':      d['T'],               
            'sample_hz': d['AHz'],             
        })

    return pd.DataFrame(records)


def imu_sample_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df['sample_hz'].median())