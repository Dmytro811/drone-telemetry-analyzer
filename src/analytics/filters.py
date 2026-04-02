import pandas as pd

def moving_average_filter(data_series, window_size=5):
    return data_series.rolling(window=window_size, min_periods=1).mean()