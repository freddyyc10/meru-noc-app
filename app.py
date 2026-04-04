import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import time
import io
from PIL import Image

# --- CONFIGURACIÓN DE LA PLATAFORMA ---
API_KEY = ""  # Se inyecta automáticamente en el entorno
MODEL_TEXT = "gemini-2.5-flash-preview-09-2025"
MODEL_IMAGE = "gemini-2.5-flash-image-preview"

# --- FUNCIONES DE ANÁLISIS LOCAL (IA ESTADÍSTICA) ---
def detect_anomalies(data):
    """Detecta anomalías usando Z-Score (3 desviaciones estándar)."""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0: return []
    z_scores = [(y - mean) / std for y in data]
    return np.where(np.abs(z_scores) > 2.5)[0]

# --- FUNCIONES DE IA GENERATIVA (VISIÓN) ---
def analyze_with_visual_ai(df, metric_name):
    """
    Genera un gráfico, lo convierte en imagen y pide a la IA que lo analice 
    como si fuera un operador humano mirando una pantalla.
    """
    # 1. Crear el gráfico técnico para la IA
    fig = px.line(df, y=metric_name, title=f"Telemetría Crítica: {metric_name}", 
                  template="plotly_dark", color_discrete_sequence=['#00ff00'])
    img_bytes = fig.to_image(format="png", width=800, height=400)
    base64_image = base64.b64encode(img_bytes).decode('utf-8')

    # 2. Llamada a Gemini Image
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IMAGE}:generateContent?key={API_KEY}"
    
    prompt = f"""
    Actúa como un Ingeniero Senior de Ciberseguridad en un NOC.
    Analiza esta imagen de telemetría de red:
    1. Identifica patrones visuales de ataques (DDoS, escaneo de puertos) o fallos de enlace.
    2. Explica la severidad basándote en la forma de los picos.
    3. Da una recomendación de mitigación inmediata.
    Responde en español de forma concisa.
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/png", "data": base64_image}}
            ]
        }],
        "generationConfig": { "responseModalities": ["TEXT"] }
    }

    # Exponential Backoff
    for delay in [1, 2, 4]:
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            time.sleep(delay)
        except:
            time.sleep(delay)
    
    return "⚠️ El motor visual no pudo procesar la imagen. Revise el análisis estadístico local."

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Meru Network Intelligence", layout="wide", page_icon="📡")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #e0e0e0; }
    .metric-card { 
        background: #0f172a; border: 1px solid #1e293b; 
        padding: 15px; border-radius: 10px; text-align: center;
    }
    .status-online { color: #10b981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Encabezado pro
col_header, col_status = st.columns([4, 1])
with col_header:
    st.title("📡 Meru Intel Center")
    st.write("SISTEMA DE MONITOREO PROACTIVO DE CAPA 3")
with col_status:
    st.markdown('<p class="status-online">● SISTEMA OPERATIVO</p>', unsafe_allow_html=True)
    st.caption(f"Kernel: {MODEL_TEXT}")

# Carga de datos
uploaded_file = st.sidebar.file_uploader("📂 Importar Log de Telemetría (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    selected_metric = st.sidebar.selectbox("Seleccionar Métrica de Análisis", numeric_cols)
    
    # Grid Principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico Interactivo
        st.subheader(f"Flujo de Datos: {selected_metric}")
        indices_anomalias = detect_anomalies(df[selected_metric])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[selected_metric], name="Tráfico Nominal", line=dict(color='#00d4ff')))
        
        if len(indices_anomalias) > 0:
            fig.add_trace(go.Scatter(
                x=indices_anomalias, 
                y=df[selected_metric].iloc[indices_anomalias],
                mode='markers', name='ANOMALÍA DETECTADA',
                marker=dict(color='red', size=10, symbol='x')
            ))
        
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⚡ Diagnóstico de IA")
        
        if st.button("🚀 Ejecutar Escaneo Visual"):
            with st.spinner("IA analizando patrones visuales de tráfico..."):
                visual_report = analyze_with_visual_ai(df, selected_metric)
                st.info(visual_report)
        
        st.divider()
        st.subheader("📊 Estadísticas de Capa")
        avg = df[selected_metric].mean()
        max_v = df[selected_metric].max()
        st.metric("Promedio de Carga", f"{avg:.2f}")
        st.metric("Picos Identificados", len(indices_anomalias))
        
        if len(indices_anomalias) > 5:
            st.error("ALERTA: Patrón de inestabilidad detectado. Iniciar protocolo de mitigación.")

    # Tabla de logs críticos
    with st.expander("Ver Datos Crudos y Logs de Eventos"):
        st.dataframe(df, use_container_width=True)

else:
    # Estado inicial / Demo
    st.info("Esperando flujo de datos... Por favor, carga un archivo de telemetría en el panel lateral.")
    
    # Generar datos simulados para demo rápida
    if st.button("Generar Datos de Prueba"):
        t = np.linspace(0, 100, 100)
        y = 50 + 10*np.sin(t/5) + np.random.normal(0, 5, 100)
        y[30:35] = 180 # Simular ataque
        demo_df = pd.DataFrame({'minutos': t, 'trafico_gbps': y})
        st.session_state['demo_data'] = demo_df
        st.write("Demo generada. Descarga este CSV para probar:")
        st.download_button("Descargar Demo CSV", demo_df.to_csv(index=False), "demo_network.csv")
