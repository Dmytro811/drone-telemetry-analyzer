import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
from src.core.pipeline import run_pipeline

st.title("Drone Telemetry Speed Visualizer")

uploaded_file = st.file_uploader("Upload Ardupilot log file (.bin or .log)", type=['bin', 'log'])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_file_path = temp_file.name
    
    # Parse the log
    data = run_pipeline(temp_file_path)
    
    if 'gps' in data and not data['gps'].empty:
        gps_df = data['gps']
        
        # Plot speed over time
        fig, ax = plt.subplots()
        ax.plot(gps_df['timestamp'], gps_df['spd'])
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Speed (m/s)')
        ax.set_title('Horizontal Speed Over Time')
        
        st.pyplot(fig)
    else:
        st.error("No GPS data found in the log file.")
    
    # Clean up temp file
    try:
        os.unlink(temp_file_path)
    except PermissionError:
        pass  # File might still be in use, will be cleaned up later