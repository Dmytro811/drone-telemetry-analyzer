import pandas as pd
import numpy as np
from pymavlink import mavutil


def parse_log(file_path: str) -> dict[str, pd.DataFrame]:
    """
    Парсить бінарний лог Ardupilot (.BIN / .log).
    Повертає словник з DataFrame для GPS та IMU даних.
    
    Повертає dict з ключами:
        'gps' - DataFrame з GPS даними
        'imu' - DataFrame з IMU даними
        'meta' - dict з метаданими (частоти семплювання, одиниці)
    """
    mav = mavutil.mavlink_connection(file_path, dialect='ardupilotmega')
    
    gps_records = []
    imu_records = []
    
    while True:
        msg = mav.recv_match(type=['GPS', 'IMU'])
        if msg is None:
            break
        
        t = msg.get_type()
        d = msg.to_dict()
        
        if t == 'GPS':
            if d.get('Status', 0) < 3:
                continue
            gps_records.append({
                'timestamp': d['TimeUS'] / 1e6,   
                'lat':       d['Lat'],
                'lon':       d['Lng'],
                'alt':       d['Alt'],             
                'spd':       d['Spd'],             
                'vz':        d['VZ'],              
                'n_sats':    d['NSats'],
                'hdop':      d['HDop'],
            })
        elif t == 'IMU':
            imu_records.append({
                'timestamp': d['TimeUS'] / 1e6,
                'acc_x':     d['AccX'],            
                'acc_y':     d['AccY'],
                'acc_z':     d['AccZ'],
                'gyr_x':     d['GyrX'],            
                'gyr_y':     d['GyrY'],
                'gyr_z':     d['GyrZ'],
                'sample_hz': d['AHz'],             
            })
    
    gps_df = pd.DataFrame(gps_records)
    imu_df = pd.DataFrame(imu_records)
    
    
    meta = {
        'gps_hz': _calc_sample_rate(gps_df['timestamp']),
        'imu_hz': imu_df['sample_hz'].median() if not imu_df.empty else 0,
        'gps_units': {'lat': 'deg', 'lon': 'deg', 'alt': 'm', 'spd': 'm/s'},
        'imu_units': {'acc': 'm/s²', 'gyr': 'rad/s'},
    }
    
    return {'gps': gps_df, 'imu': imu_df, 'meta': meta}


def _calc_sample_rate(timestamps: pd.Series) -> float:
    """Обчислює середню частоту семплювання з масиву timestamp."""
    if len(timestamps) < 2:
        return 0.0
    diffs = timestamps.diff().dropna()
    return round(1.0 / diffs.median(), 2)