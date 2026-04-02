import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_echarts import st_echarts

# --- Configuración Inicial ---
st.set_page_config(page_title="Meru NOC & Talent", layout="wide", page_icon="📡")

# --- Configuración de API y Constantes ---
# El ID del modelo se maneja como string puro para evitar errores de sintaxis (09)
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = ""  # El entorno proporciona la clave automáticamente
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_ai(prompt):
    """Lógica de IA con Exponential Backoff (1s, 2s, 4s, 8s, 16s)"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "Actúa como un experto en Redes (NOC) y Reclutamiento IT. Responde de forma técnica y concisa."}]}
    }
    
    delays = [1, 2, 4, 8, 16]
    for delay in delays:
        try:
            response = requests.post(ENDPOINT, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Sin respuesta.")
            if response.status_code in [429, 500, 503]:
                time.sleep(delay)
                continue
            return f"Error API: {response.status_code}"
        except Exception as e:
            time.sleep(delay)
    return "Error: Tiempo de espera agotado tras reintentos."

# --- Generación de Datos de Ejemplo ---
def get_mock_data():
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    traffic = np.random.randint(100, 1000, size=10).tolist()
    
    candidates = pd.DataFrame({
        "ID": range(1, 6),
        "Nombre": ["Luis Rivas", "Elena Soler", "Marcos Paz", "Julia Sanz", "Kevin Oro"],
        "Rol": ["Core Engineer", "Cloud Admin", "NOC L2", "DevOps", "Cybersecurity"],
        "Score": [92, 85, 78, 95, 88],
        "Estado": ["Entrevista", "Evaluación", "Pre-seleccionado", "Oferta", "Nuevo"]
    })
    return dates, traffic, candidates

dates, traffic, candidates_df = get_mock_data()

# --- Interfaz de Usuario (Panel y Menú) ---
st.sidebar.title("🌐 Meru NOC & Talent")
menu = st.sidebar.radio("Navegación", ["Dashboard General", "Gestión de Talento", "Asistente IA"])

# --- Pantalla 1: Dashboard General (NOC) ---
if menu == "Dashboard General":
    st.header("📊 Operaciones de Red (NOC)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Uptime Global", "99.99%", "0.02%")
    col2.metric("Tickets Activos", "24", "-5")
    col3.metric("Latencia Media", "12ms", "-1ms")
    
    st.subheader("📈 Tráfico de Red (Gbps)")
    options = {
        "xAxis": {"type": "category", "data": [d.strftime("%m-%d") for d in dates]},
        "yAxis": {"type": "value"},
        "series": [{"data": traffic, "type": "line", "smooth": True, "color": "#1f77b4"}],
        "tooltip": {"trigger": "axis"}
    }
    st_echarts(options=options, height="300px")

# --- Pantalla 2: Gestión de Talento ---
elif menu == "Gestión de Talento":
    st.header("👥 Pipeline de Talento IT")
    
    gb = GridOptionsBuilder.from_dataframe(candidates_df)
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_selection('single', use_checkbox=True)
    gridOptions = gb.build()

    st.subheader("Base de Datos de Candidatos")
    grid_response = AgGrid(
        candidates_df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=True,
        theme='streamlit'
    )

# --- Pantalla 3: Asistente IA (Integración Solicitada) ---
elif menu == "Asistente IA":
    st.header("🤖 Asistente Estratégico (Gemini)")
    st.markdown("Utiliza la IA para analizar incidentes de red o evaluar perfiles de candidatos.")
    
    contexto = st.selectbox("Contexto de la consulta", ["Análisis NOC", "Evaluación Talento"])
    user_input = st.text_area("Describa la situación o pegue el CV/Log aquí:", height=200)
    
    if st.button("Consultar IA"):
        if user_input:
            with st.spinner("Analizando con Gemini 2.5 Flash..."):
                full_prompt = f"Contexto: {contexto}. Detalle: {user_input}"
                respuesta = call_gemini_ai(full_prompt)
                st.chat_message("assistant").write(respuesta)
        else:
            st.error("Por favor, ingrese información para procesar.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Versión: 2.0 | Modelo: {MODEL_NAME}")
