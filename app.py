import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import json
import time

# --- CONFIGURACIÓN DE ACCESO Y MODELO ---
# Usando la API Key de las capturas proporcionadas
API_KEY = "AlzaSyBQy0psFsocJJN5rEsiYRCi-dqOH_qDmg"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def get_ai_analysis(summary_text, detail_samples):
    """
    Función de análisis profundo de red. 
    Implementa retries con backoff exponencial para evitar errores de cuota.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    prompt = f"""
    Eres el experto senior en NOC de Meru Networks. Analiza la siguiente telemetría:
    
    RESUMEN ESTADÍSTICO:
    {summary_text}
    
    MUESTRA DE DATOS (ANOMALÍAS DETECTADAS):
    {detail_samples}
    
    TAREAS:
    1. Identifica picos de tráfico o caídas de señal.
    2. Diagnostica posibles causas (congestión, interferencia, fallo de hardware).
    3. Sugiere 3 acciones técnicas inmediatas.
    
    Responde en español con un tono profesional y técnico.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    # Reintentos automáticos
    for wait_time in [1, 2, 4, 8]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 404:
                return "❌ Error 404: El modelo especificado no está disponible. Contacta al administrador."
            elif response.status_code == 429:
                time.sleep(wait_time)
                continue
            else:
                return f"⚠️ Error del Servidor: {response.status_code}\n{response.text}"
        except Exception as e:
            return f"❌ Error de conexión: {str(e)}"
    
    return "No se pudo obtener respuesta de la IA después de varios intentos."

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Meru NOC - Dashboard", page_icon="🛰️", layout="wide")

# Estilo visual Meru Networks
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .report-container {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        font-family: 'monospace';
    }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("🛰️ Meru Intelligence Center")
    st.write("Monitoreo Avanzado y Diagnóstico por IA")

# Sidebar
st.sidebar.header("Configuración de Datos")
uploaded_file = st.sidebar.file_uploader("Cargar estadísticas (.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # --- MÉTRICAS DE NIVEL SUPERIOR ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Registros", len(df))
    with m2:
        # Intentar detectar columnas de latencia
        lat_col = [c for c in df.columns if 'lat' in c.lower() or 'ms' in c.lower()]
        if lat_col:
            st.metric("Latencia Promedio", f"{df[lat_col[0]].mean():.2f} ms")
        else:
            st.metric("Columnas", len(df.columns))
    with m3:
        st.metric("Estado de IA", "Conectado", delta="Gemini 2.5")
    with m4:
        st.metric("Servicio", "NOC Meru")

    # --- PESTAÑAS DE FUNCIONALIDAD ---
    tab_viz, tab_anom, tab_ai = st.tabs(["📊 Visualización", "🔍 Detección de Anomalías", "🧠 Informe de IA"])

    with tab_viz:
        st.subheader("Análisis de Tendencias")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            col_sel, col_graph = st.columns([1, 3])
            with col_sel:
                y_axis = st.selectbox("Métrica a visualizar", num_cols)
                chart_type = st.radio("Tipo de gráfico", ["Área", "Línea", "Barras"])
            
            with col_graph:
                if chart_type == "Área":
                    st.plotly_chart(px.area(df, y=y_axis, template="plotly_dark"), use_container_width=True)
                elif chart_type == "Línea":
                    st.plotly_chart(px.line(df, y=y_axis, template="plotly_dark"), use_container_width=True)
                else:
                    st.plotly_chart(px.bar(df, y=y_axis, template="plotly_dark"), use_container_width=True)

    with tab_anom:
        st.subheader("Puntos Críticos Detectados")
        if num_cols:
            # Detectar valores por encima del percentil 95
            threshold = st.slider("Umbral de Anomalía (Percentil)", 90, 99, 95)
            val_threshold = np.percentile(df[num_cols[0]], threshold)
            anomalies = df[df[num_cols[0]] > val_threshold]
            
            st.write(f"Registros que superan el umbral de {val_threshold:.2f}:")
            st.dataframe(anomalies, use_container_width=True)

    with tab_ai:
        st.subheader("Generador de Reporte Predictivo")
        if st.button("🪄 Analizar con IA"):
            with st.spinner("Procesando telemetría con Gemini..."):
                summary = df.describe().to_string()
                # Tomamos los 15 registros más altos para que la IA los vea
                samples = df.sort_values(by=num_cols[0], ascending=False).head(15).to_string()
                
                report = get_ai_analysis(summary, samples)
                
                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(report)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button("Descargar Reporte", report, "meru_ai_report.txt")

else:
    st.info("Carga un archivo CSV para activar el panel de control.")
    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1000", caption="Conectividad Global Meru")
