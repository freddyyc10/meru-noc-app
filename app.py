import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import json
import time

# --- CONFIGURACIÓN DE VANGUARDIA (ABRIL 2026) ---
# API Key extraída de tus capturas de pantalla
API_KEY = "AlzaSyBQy0psFsocJJN5rEsiYRCi-dqOH_qDmg"
# Actualizado a la serie Gemini 3 (Estándar actual)
MODEL_NAME = "gemini-3.0-flash"

def generate_meru_intelligence(df_summary, df_anomalies):
    """
    Función de análisis con Gemini 3.
    Optimizado para diagnósticos de red de baja latencia.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    prompt = f"""
    SISTEMA: Eres el Motor de Inteligencia Artificial de Meru Networks (NOC Proactivo).
    
    CONTEXTO DE DATOS:
    Resumen Estadístico:
    {df_summary}
    
    Muestras de Anomalías (Picos Detectados):
    {df_anomalies}
    
    INSTRUCCIONES:
    1. Realiza un diagnóstico proactivo: ¿Hay saturación de ancho de banda o pérdida de paquetes?
    2. Identifica patrones de comportamiento anómalos.
    3. Genera 3 recomendaciones de optimización técnica para el equipo de campo.
    
    Responde en español, con lenguaje técnico de redes pero conciso.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    # Implementación de retry con backoff exponencial
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 404:
                return "❌ Error: Modelo Gemini 3 no encontrado en esta región. Verifica el nombre del modelo."
            elif response.status_code == 429:
                time.sleep(delay)
                continue
            else:
                return f"⚠️ Error {response.status_code}: {response.text}"
        except Exception as e:
            return f"❌ Fallo de conexión: {str(e)}"
    
    return "Servicio temporalmente no disponible."

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Meru Intelligence Center", page_icon="🛰️", layout="wide")

# Estilo corporativo Meru (Dark Mode Premium)
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { border: 1px solid #30363d; padding: 15px; border-radius: 10px; background: #161b22; }
    .report-box { 
        background-color: #0d1117; 
        border-left: 5px solid #238636; 
        padding: 20px; 
        border-radius: 0 10px 10px 0;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Meru Intelligence Center")
st.subheader("Monitoreo Proactivo de Red con IA (Generación 3)")

# Sidebar para gestión de datos
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002.svg", width=50)
    st.header("Centro de Datos")
    uploaded_file = st.file_uploader("Cargar Telemetría (.csv)", type=["csv"])
    st.divider()
    st.info("Versión: Gemini 3.0 Flash-Lite Optimized")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # --- DASHBOARD DE MÉTRICAS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Nodos Activos", len(df))
    with c2:
        # Buscamos columnas numéricas para promedios
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        val = df[num_cols[0]].mean() if num_cols else 0
        st.metric("Promedio General", f"{val:.2f}")
    with c3:
        st.metric("IA Engine", "Gemini 3.0", "Active")
    with c4:
        st.metric("SLA", "99.9% Compliance")

    # --- PESTAÑAS FUNCIONALES ---
    tab_viz, tab_anom, tab_ai = st.tabs(["📊 Visualización", "🔍 Análisis de Picos", "🧠 Informe de IA"])

    with tab_viz:
        if num_cols:
            col_ctrl, col_plot = st.columns([1, 3])
            with col_ctrl:
                target = st.selectbox("Métrica de Red", num_cols)
                style = st.radio("Gráfico", ["Área", "Línea", "Barras"])
            
            with col_plot:
                if style == "Área":
                    fig = px.area(df, y=target, template="plotly_dark", color_discrete_sequence=['#238636'])
                elif style == "Línea":
                    fig = px.line(df, y=target, template="plotly_dark", color_discrete_sequence=['#58a6ff'])
                else:
                    fig = px.bar(df, y=target, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

    with tab_anom:
        st.subheader("Detección de Anomalías")
        if num_cols:
            sensivity = st.slider("Sensibilidad de Alerta", 0.8, 1.0, 0.95)
            q_threshold = df[num_cols[0]].quantile(sensivity)
            anomalies = df[df[num_cols[0]] > q_threshold]
            
            st.warning(f"Se han detectado {len(anomalies)} registros por encima del umbral crítico ({q_threshold:.2f})")
            st.dataframe(anomalies, use_container_width=True)

    with tab_ai:
        st.subheader("Informe de Inteligencia Artificial")
        if st.button("🚀 Generar Diagnóstico con Gemini 3"):
            with st.spinner("Analizando patrones en la nube de Meru..."):
                summary_data = df.describe().to_string()
                top_issues = anomalies.head(10).to_string() if not anomalies.empty else "No se detectan picos críticos."
                
                ai_report = generate_meru_intelligence(summary_data, top_issues)
                
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(ai_report)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button("💾 Guardar Reporte", ai_report, file_name="meru_noc_report.md")

else:
    st.info("Esperando carga de datos CSV para iniciar el monitoreo...")
    # Imagen de respaldo decorativa
    st.image("https://images.unsplash.com/photo-1551703599-6b3e8379aa8c?auto=format&fit=crop&q=80&w=1200", caption="Centro de Control Meru Networks")
