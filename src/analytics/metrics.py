import numpy as np
import pandas as pd
from .haversine import Haversine

class AnalyticsCore:
    def __init__(self, df_gps, df_imu):
        """
        Ініціалізація ядра аналітики.
        df_gps: DataFrame з колонками [timestamp, lat, lon, alt, spd, vz]
        df_imu: DataFrame з колонками [timestamp, acc_x, acc_y, acc_z]
        """
        self.df_gps = df_gps
        self.df_imu = df_imu

    def calculate_metrics(self):
        """
        Розраховує основні польотні показники, комбінуючи дані GPS та IMU.
        """
        if self.df_gps.empty or self.df_imu.empty:
            return {}

        # 1. ЧАС ТА ДИСТАНЦІЯ
        t_gps = self.df_gps['timestamp'].values
        # Перетворюємо мікросекунди в секунди, якщо дані у форматі ArduPilot
        if t_gps.max() > 1_000_000:
            t_gps = t_gps / 1_000_000.0
        
        total_time = t_gps[-1] - t_gps[0]

        # Дистанція по Хаверсину (враховує кривизну Землі)
        lats = self.df_gps['lat'].values
        lons = self.df_gps['lon'].values
        total_distance = Haversine(lats, lons)

        # 2. ВИСОТА
        # Максимальний набір висоти відносно точки зльоту
        max_alt_gain = self.df_gps['alt'].max() - self.df_gps['alt'].iloc[0]

        # 3. ШВИДКІСТЬ (Беремо з GPS для уникнення дрейфу інтегрування)
        # Горизонтальна швидкість (колонка spd в логах ArduPilot)
        max_horizontal_speed = self.df_gps['spd'].max()
        
        # Вертикальна швидкість (колонка vz)
        if 'vz' in self.df_gps:
            max_vertical_speed = np.abs(self.df_gps['vz']).max()
        else:
            # Якщо vz немає, рахуємо як зміну висоти / час
            alt_diff = np.diff(self.df_gps['alt'].values)
            time_diff = np.diff(t_gps)
            max_vertical_speed = np.max(np.abs(alt_diff / time_diff))

        # 4. ПРИСКОРЕННЯ (Беремо з IMU + Фільтрація)
        # Отримуємо сирі дані
        acc_x = self.df_imu['acc_x'].values
        acc_y = self.df_imu['acc_y'].values
        acc_z = self.df_imu['acc_z'].values

        # ТЕОРЕТИЧНЕ ОБҐРУНТУВАННЯ: 
        # Використовуємо High-pass filter (ковзне середнє), щоб відсікти "Gravity Leakage".
        # Це дозволяє отримати чисте динамічне прискорення без впливу нахилу дрона.
        window = 50 
        clean_x = acc_x - pd.Series(acc_x).rolling(window=window, min_periods=1).mean().values
        clean_y = acc_y - pd.Series(acc_y).rolling(window=window, min_periods=1).mean().values
        clean_z = acc_z - pd.Series(acc_z).rolling(window=window, min_periods=1).mean().values

        # Векторна сума горизонтального прискорення
        accel_h = np.sqrt(clean_x**2 + clean_y**2)
        # Максимальне загальне прискорення (враховуємо і вертикальні ривки)
        max_acceleration = max(accel_h.max(), np.abs(clean_z).max())

        return {
            "Тривалість польоту (с)": float(total_time),
            "Пройдена дистанція (м)": float(total_distance),
            "Макс. набір висоти (м)": float(max_alt_gain),
            "Макс. прискорення (м/с²)": float(max_acceleration),
            "Макс. гориз. швидкість (м/с)": float(max_horizontal_speed),
            "Макс. вертик. швидкість (м/с)": float(max_vertical_speed)
        }