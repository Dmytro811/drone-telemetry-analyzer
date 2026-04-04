import streamlit as st
import pandas as pd
import tempfile
import os
from src.core.pipeline import run_pipeline
from src.visualization.enu_converter import convert_to_enu
from src.visualization.plot_3d import plot_3d_trajectory

st.title("Drone Telemetry 3D Trajectory Visualizer")

uploaded_file = st.file_uploader("Upload Ardupilot log file (.bin or .log)", type=['bin', 'log'])

color_by = st.selectbox("Color trajectory by:", ["spd", "timestamp"])

if uploaded_file is not None:
    # зберігаємо завантажений файл тимчасово
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_file_path = temp_file.name
    
    # парс
    data = run_pipeline(temp_file_path)
    
    if 'gps' in data and not data['gps'].empty:
        gps_df = data['gps']
        
        enu_df = convert_to_enu(gps_df)

        fig = plot_3d_trajectory(enu_df, color_by=color_by)
        if fig:
            st.plotly_chart(fig)
        else:
            st.error("Failed to generate 3D plot.")
    else:
        st.error("No GPS data found in the log file.")
    
    try:
        os.unlink(temp_file_path)
    except PermissionError:
        pass  # якщо файл використовується то пропускаєм, система потім видалить сама