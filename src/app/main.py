import sys
import os

# Додаємо корінь проєкту в шлях пошуку модулів
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import tempfile
import matplotlib.pyplot as plt
import google.generativeai as genai

# Імпорт твоїх розробок
from src.core.pipeline import run_pipeline
from src.visualization.enu_converter import convert_to_enu
from src.visualization.plot_3d import plot_3d_trajectory
from src.analytics.metrics import AnalyticsCore
from src.analytics.drone_configs import DRONE_MODELS  # <--- ІМПОРТ КОНФІГУРАЦІЇ

# Налаштування інтерфейсу
st.set_page_config(page_title="Drone Telemetry Analyzer", layout="wide", initial_sidebar_state="expanded")

# --- БІЧНА ПАНЕЛЬ ---
st.sidebar.title("🎮 Керування")
page = st.sidebar.radio("Режим перегляду:", ["Головний Дашборд", "Детальний графік швидкості", "Дані (Таблиці)"])

st.sidebar.divider()
st.sidebar.subheader("⚙️ Параметри БПЛА")

# Використовуємо ключі зі словника для списку вибору
drone_options = ["Не вибрано"] + list(DRONE_MODELS.keys())
drone_type = st.sidebar.selectbox("Оберіть модель дрона:", drone_options)

st.sidebar.divider()
st.sidebar.subheader("🤖 Налаштування AI")
api_key = st.sidebar.text_input("Gemini API Key:", type="password")
st.sidebar.caption("[Отримати ключ тут](https://aistudio.google.com/app/apikey)")

st.sidebar.divider()
uploaded_file = st.sidebar.file_uploader("Завантажте лог (.BIN або .LOG)", type=['bin', 'log'])

# --- ГОЛОВНИЙ ЕКРАН ---
st.title("Аналізатор Телеметрії Дрона ")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_file_path = temp_file.name
    
    try:
        with st.spinner('Обробка даних телеметрії...'):
            data = run_pipeline(temp_file_path)
        
        if 'gps' in data and not data['gps'].empty and 'imu' in data and not data['imu'].empty:
            gps_df = data['gps']
            imu_df = data['imu']
            
            analytics = AnalyticsCore(df_gps=gps_df, df_imu=imu_df)
            metrics = analytics.calculate_metrics()
            
            if page == "Головний Дашборд":
                st.subheader(" Ключові показники польоту")
                c1, c2, c3 = st.columns(3)
                c1.metric("Час польоту", f"{metrics['Тривалість польоту (с)']:.1f} с")
                c2.metric("Дистанція", f"{metrics['Пройдена дистанція (м)']:.1f} м")
                c3.metric("Макс. висота", f"{metrics['Макс. набір висоти (м)']:.1f} м")
                
                c4, c5, c6 = st.columns(3)
                c4.metric("Макс. прискорення", f"{metrics['Макс. прискорення (м/с²)']:.2f} м/с²")
                c5.metric("Макс. гориз. швидкість", f"{metrics['Макс. гориз. швидкість (м/с)']:.1f} м/с")
                c6.metric("Макс. вертик. швидкість", f"{metrics['Макс. вертик. швидкість (м/с)']:.1f} м/с")
                
                # --- РОЗРАХУНОК ВИТРАТ (Тепер беремо дані з окремого файлу) ---
                if drone_type != "Не вибрано":
                    st.divider()
                    st.subheader("⛽ Споживання енергії / пального")
                    
                    d_info = DRONE_MODELS[drone_type]
                    total_time_sec = metrics['Тривалість польоту (с)']
                    total_consumption = total_time_sec * d_info['rate']
                    
                    c7, c8 = st.columns([1, 3])
                    c7.metric(f"Витрачено ({d_info['unit']})", f"{total_consumption:.1f} {d_info['unit']}")
                    c8.info(f"{d_info['icon']} **Аналітика для: {drone_type}** \n{d_info['desc']}.")
                
                st.divider()
                
                st.subheader("🤖 AI Аналіз польоту")
                if st.button("Проаналізувати за допомогою ШІ", type="primary"):
                    if not api_key:
                        st.warning("Будь ласка, введіть API ключ.")
                    else:
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            prompt = f"Проаналізуй дані БПЛА: Час {metrics['Тривалість польоту (с)']:.1f}с, Дистанція {metrics['Пройдена дистанція (м)']:.1f}м. Напиши висновок."
                            response = model.generate_content(prompt)
                            st.info(response.text)
                        except Exception as e:
                            st.error(f"Помилка AI: {e}")
                
                st.divider()
                
                st.subheader("🗺️ 3D Траєкторія (ENU)")
                color_option = st.selectbox("Колір лінії за:", ["spd", "timestamp"])
                enu_df = convert_to_enu(gps_df)
                fig = plot_3d_trajectory(enu_df, color_by=color_option)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

            elif page == "Детальний графік швидкості":
                st.subheader("📈 Зміна горизонтальної швидкості")
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(gps_df['timestamp'], gps_df['spd'], color='#00d4ff', linewidth=2)
                fig.patch.set_facecolor('#0e1117')
                ax.set_facecolor('#0e1117')
                ax.tick_params(colors='white')
                st.pyplot(fig)
            
            elif page == "Дані (Таблиці)":
                st.subheader("🗄️ Сирі дані телеметрії")
                tab1, tab2 = st.tabs([" Дані GPS", " Дані IMU"])
                with tab1: st.dataframe(gps_df, use_container_width=True)
                with tab2: st.dataframe(imu_df, use_container_width=True)
                
    except Exception as e:
        st.error(f"Виникла помилка: {e}")
    finally:
        if os.path.exists(temp_file_path):
            try: os.unlink(temp_file_path)
            except: pass
else:
    st.info(" Завантажте файл телеметрії в меню зліва.")