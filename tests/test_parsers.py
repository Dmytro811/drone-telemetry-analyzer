"""
Запуск: python -m tests.test_parsers
"""
from src.parser.gps_parser import extract_gps, gps_sample_rate
from src.parser.imu_parser import extract_imu, imu_sample_rate

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

if __name__ == "__main__":
    test_gps()
    test_imu()