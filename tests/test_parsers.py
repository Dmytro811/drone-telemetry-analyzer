"""
Запуск: python -m tests.test_parsers
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parser.gps_parser import extract_gps, gps_sample_rate
from src.parser.imu_parser import extract_imu, imu_sample_rate

import pandas as pd
import numpy as np
from src.analytics.metrics import AnalyticsCore
LOG_FILE = "data/raw/00000001.BIN"  # або повний шлях

def test_gps():
    df = extract_gps(LOG_FILE)
    print("=== GPS ===")
    print(f"Рядків: {len(df)}")
    print(f"Колонки: {list(df.columns)}")
    print(f"Частота: {gps_sample_rate(df)} Гц")
    print(f"Координати: lat=[{df['lat'].min():.5f}, {df['lat'].max():.5f}]")
    print(f"            lon=[{df['lon'].min():.5f}, {df['lon'].max():.5f}]")
    print(f"Висота: min={df['alt'].min():.1f}м, max={df['alt'].max():.1f}м")
    print(df.head())
    print()

def test_imu():
    df = extract_imu(LOG_FILE, instance=0)
    print("=== IMU ===")
    print(f"Рядків: {len(df)}")
    print(f"Колонки: {list(df.columns)}")
    print(f"Частота: {imu_sample_rate(df)} Гц")
    print(f"AccZ (спокій ≈ -9.8): mean={df['acc_z'].mean():.3f} м/с²")
    
    print(df.head())

def test_analytics_core():
    print("=== АНАЛІТИКА (ЯДРО) ===")
    mock_data = {
        'time': [0.0, 1.0, 2.0, 3.0],
        'lat': [50.4501, 50.4502, 50.4503, 50.4504],
        'lon': [30.5234, 30.5234, 30.5234, 30.5234],
        'alt': [100.0, 105.0, 110.0, 108.0],
        'accel_x': [0.5, 1.0, -0.5, 0.0],
        'accel_y': [0.1, 0.2, 0.1, 0.0],
        'accel_z': [1.0, 2.0, 0.0, -1.0]
        
    }
    df_mock = pd.DataFrame(mock_data)
    
    try:
        analyzer = AnalyticsCore(df_mock)
        results = analyzer.calculate_metrics()
        
        print("УСПІХ! Ядро працює. Результати:")
        for key, value in results.items():
            print(f"  {key:<30}: {value:.4f}")
    except Exception as e:
        print(f"ПОМИЛКА в ядрі аналітики: {e}")

def test_real_mission_analytics():
    print("=== АНАЛІЗ РЕАЛЬНОЇ МІСІЇ (00000001.BIN) ===")
    try:
        # Твої функції екстракції даних
        df_gps = extract_gps(LOG_FILE)
        df_imu = extract_imu(LOG_FILE, instance=0)
        
        if df_gps.empty or df_imu.empty:
            print("Помилка: один із датафреймів порожній.")
            return

        # Запуск ядра
        analyzer = AnalyticsCore(df_gps, df_imu)
        results = analyzer.calculate_metrics()
        
        print("Розрахунок завершено успішно:")
        print("-" * 45)
        for key, value in results.items():
            print(f"{key:<32}: {value:.2f}")
        print("-" * 45)
        
    except Exception as e:
        print(f"Помилка аналітики: {e}")

if __name__ == "__main__":
    test_gps()
    test_imu()
    test_real_mission_analytics()
