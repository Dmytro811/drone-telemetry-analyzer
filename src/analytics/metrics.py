import numpy as np
import pandas as pd
from .haversine import Haversine
from .integration import trapezoidal_integration

class AnalyticsCore:
    def __init__(self, df_gps, df_imu):
        self.df_gps = df_gps
        self.df_imu = df_imu

    def calculate_metrics(self):
        t_imu = self.df_imu['timestamp'].values
        if t_imu.max() > 1000000:
            t_imu = t_imu / 1_000_000.0

        t_gps = self.df_gps['timestamp'].values
        if t_gps.max() > 1000000:
            t_gps = t_gps / 1_000_000.0

        total_time = t_imu[-1] - t_imu[0]
        max_alt_gain = (self.df_gps['alt'].max() - self.df_gps['alt'].min()) / 100.0

        offset_x = np.mean(self.df_imu['acc_x'].values[:100])
        offset_y = np.mean(self.df_imu['acc_y'].values[:100])
        offset_z = np.mean(self.df_imu['acc_z'].values[:100])

        clean_acc_x = self.df_imu['acc_x'].values - offset_x
        clean_acc_y = self.df_imu['acc_y'].values - offset_y
        clean_acc_z = self.df_imu['acc_z'].values - offset_z

        accel_h = np.sqrt(clean_acc_x**2 + clean_acc_y**2)
        max_acceleration = max(accel_h.max(), np.abs(clean_acc_z).max())

        lats = self.df_gps['lat'].values
        lons = self.df_gps['lon'].values
        total_distance = Haversine(lats, lons)

        vel_x = trapezoidal_integration(t_imu, clean_acc_x)
        vel_y = trapezoidal_integration(t_imu, clean_acc_y)
        
        horizontal_velocities = np.sqrt(vel_x**2 + vel_y**2)
        vertical_velocities = trapezoidal_integration(t_imu, clean_acc_z)

        max_horizontal_speed = np.max(np.abs(horizontal_velocities))
        max_vertical_speed = np.max(np.abs(vertical_velocities))

        return {
            "Тривалість польоту (с)": total_time,
            "Пройдена дистанція (м)": total_distance,
            "Макс. набір висоти (м)": max_alt_gain,
            "Макс. прискорення (м/с²)": max_acceleration,
            "Макс. гориз. швидкість (м/с)": max_horizontal_speed,
            "Макс. вертик. швидкість (м/с)": max_vertical_speed
        }