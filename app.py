import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import json
import time

# --- CONFIGURACIÓN DE ENTORNO (ABRIL 2026) ---
# Dejamos la clave vacía para que el entorno la provea o el usuario la ingrese
API_KEY = "" 
MODEL_NAME = "gemini-3.1-flash-lite"

def generate_meru_intelligence(df_summary, df_anomalies, user_key):
    """
    Función de análisis con Gemini 3.0.
    Implementa backoff exponencial para manejar límites de cuota.
    """
    key_to_use = user_key if user_key else API_KEY
    if not key_to_use:
        return "❌ Error: No se ha detectado una API Key válida en la configuración o el panel."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={key_to_use}"
    
    prompt = f"""
    SISTEMA: Motor de IA Meru Networks (NOC Proactivo).
    DATOS TELEMETRÍA:
    Resumen: {df_summary}
    Picos críticos detectados: {df_anomalies}
    
    INSTRUCCIONES:
    Genera un diagnóstico técnico proactivo sobre el estado de la red. 
    Identifica si los picos sugieren saturación o fallas de hardware.
    Provee 3 pasos de mitigación inmediata en español.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    # Reintentos automáticos (Backoff exponencial)
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 400:
                return f"❌ Error 400: La API Key parece ser inválida. Por favor, revísala en el panel lateral."
            elif response.status_code == 429: # Límite de cuota
                time.sleep(delay)
                continue
            else:
                return f"⚠️ Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"❌ Error de conexión: {str(e)}"
    
    return "El servicio no respondió tras varios intentos."

# --- INTERFAZ UI ---
st.set_page_config(page_title="Meru Intelligence Center", page_icon="🛰️", layout="wide")

# Estética corporativa (CSS Personalizado)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { 
        background: #161b22; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #30363d;
        line-height: 1.6;
    }
    .metric-box {
        background: #21262d;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Meru Intelligence Center")
st.caption("Monitoreo en Tiempo Real | Powered by Gemini 3.0 Series")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    input_key = st.text_input("Ingresa tu API Key (opcional si ya está configurada)", type="password")
    st.divider()
    uploaded_file = st.file_uploader("Cargar Datos de Red (CSV)", type=["csv"])
    if uploaded_file:
        st.success("Archivo cargado correctamente.")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # KPIs Rápidos
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total Muestras", len(df))
    with kpi2:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        main_metric = numeric_cols[0] if numeric_cols else None
        if main_metric:
            st.metric(f"Promedio {main_metric}", f"{df[main_metric].mean():.2f}")
    with kpi3:
        st.metric("Estado de IA", "Conectado", delta="Gemini 3.0")

    # Tabs
    tab_graf, tab_picos, tab_ia = st.tabs(["📊 Gráficos Proactivos", "🔍 Análisis de Picos", "🧠 Diagnóstico IA"])

    with tab_graf:
        if main_metric:
            fig = px.area(df, y=main_metric, title=f"Tendencia de {main_metric}", 
                          template="plotly_dark", color_discrete_sequence=['#238636'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No se encontraron columnas numéricas para graficar.")

    with tab_picos:
        st.subheader("Detección de Anomalías Críticas")
        if main_metric:
            umbral = st.slider("Sensibilidad de Alerta (%)", 80, 99, 95)
            valor_umbral = df[main_metric].quantile(umbral/100)
            anomalias = df[df[main_metric] > valor_umbral]
            
            st.error(f"Se detectaron {len(anomalias)} registros que exceden el umbral de {valor_umbral:.2f}")
            st.dataframe(anomalias, use_container_width=True)

    with tab_ia:
        st.subheader("Generación de Informe Predictivo")
        if st.button("🚀 Iniciar Análisis con Gemini 3"):
            with st.spinner("Procesando telemetría..."):
                summary = df.describe().to_string()
                peaks = anomalias.head(5).to_string() if not anomalias.empty else "Estable"
                
                reporte = generate_meru_intelligence(summary, peaks, input_key)
                
                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.markdown(reporte)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button("💾 Exportar Reporte (.txt)", reporte, "reporte_meru.txt")

else:
    st.info("Por favor, sube un archivo CSV de telemetría para comenzar el análisis.")
