import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import base64
import time
import io

# --- CONFIGURACIÓN DE LA PLATAFORMA ---
API_KEY = ""  # Se inyecta automáticamente en el entorno
MODEL_TEXT = "gemini-2.5-flash-preview-09-2025"
MODEL_IMAGE = "gemini-2.5-flash-image-preview"

# --- FUNCIONES DE ANÁLISIS LOCAL ---
def detect_anomalies(data):
    """Detecta anomalías usando Z-Score (desviación estándar)."""
    mean = np.mean(data)
    std = np.std(data)
    if std < 0.001: return [] # Evitar división por cero
    z_scores = [(y - mean) / std for y in data]
    return np.where(np.abs(z_scores) > 2.5)[0]

# --- NUEVO MOTOR VISUAL ROBUSTO (SIN KALEIDO) ---
def analyze_with_visual_ai(df, metric_name):
    """
    Usa Matplotlib para generar la imagen de forma estable 
    y la envía a Gemini para visión artificial.
    """
    try:
        # 1. Crear el gráfico técnico usando Matplotlib (altamente estable)
        plt.style.use('dark_background')
        fig_plt, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df[metric_name], color='#00ff00', linewidth=1.5)
        ax.set_title(f"Network Telemetry: {metric_name}", color='#00d4ff')
        ax.grid(True, alpha=0.2)
        
        # Guardar en buffer de memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig_plt)
        buf.seek(0)
        
        base64_image = base64.b64encode(buf.read()).decode('utf-8')

        # 2. Llamada a Gemini Image
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IMAGE}:generateContent?key={API_KEY}"
        
        prompt = f"""
        Actúa como un experto en ciberseguridad. Analiza esta gráfica de tráfico de red ({metric_name}).
        - ¿Ves picos que sugieran ataques DDoS o escaneos?
        - ¿La tendencia es normal o hay degradación?
        Responde en español de forma profesional y técnica.
        """

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": "image/png", "data": base64_image}}
                ]
            }]
        }

        # Reintentos con Backoff
        for delay in [1, 2]:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            time.sleep(delay)
            
        return "⚠️ Error de comunicación con el motor de IA."
    except Exception as e:
        return f"❌ Error en el motor de visión: {str(e)}"

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Meru Intel Center", layout="wide", page_icon="📡")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #e0e6ed; }
    .status-bar { padding: 10px; border-radius: 5px; background: #1a2234; border-left: 5px solid #00d4ff; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Meru Network Intelligence")
st.markdown('<div class="status-bar">SISTEMA DE ANÁLISIS HÍBRIDO (ESTADÍSTICO + VISIÓN ARTIFICIAL)</div>', unsafe_allow_html=True)
st.write("")

# Panel Lateral
st.sidebar.header("Control de Telemetría")
uploaded_file = st.sidebar.file_uploader("Subir Log de Red (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("El archivo no contiene columnas numéricas para analizar.")
    else:
        selected_metric = st.sidebar.selectbox("Métrica a Monitorear", numeric_cols)
        
        col_viz, col_ai = st.columns([2, 1])
        
        with col_viz:
            st.subheader("Visualización en Tiempo Real")
            indices_anomalias = detect_anomalies(df[selected_metric])
            
            # Gráfico interactivo para el humano
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[selected_metric], name="Flujo", line=dict(color='#00d4ff', width=2)))
            
            if len(indices_anomalias) > 0:
                fig.add_trace(go.Scatter(
                    x=indices_anomalias, 
                    y=df[selected_metric].iloc[indices_anomalias],
                    mode='markers', name='ANOMALÍA',
                    marker=dict(color='#ff4b4b', size=10, symbol='circle-open')
                ))
            
            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col_ai:
            st.subheader("Cerebro IA")
            if st.button("🔍 Analizar Patrones Visuales", use_container_width=True):
                with st.spinner("Escaneando gráfico con Visión Artificial..."):
                    analisis = analyze_with_visual_ai(df, selected_metric)
                    st.markdown(f"**Diagnóstico:**\n\n{analisis}")
            
            st.divider()
            st.metric("Promedio de Carga", f"{df[selected_metric].mean():.2f}")
            st.metric("Eventos Críticos", len(indices_anomalias))
            
            if len(indices_anomalias) > 0:
                st.warning(f"Se han detectado {len(indices_anomalias)} puntos fuera de la desviación estándar permitida.")

else:
    # Pantalla de bienvenida
    st.info("👋 Bienvenido al Centro de Inteligencia. Por favor, sube un archivo CSV para comenzar el análisis.")
    
    if st.button("Generar Datos de Simulación"):
        t = np.arange(0, 100)
        # Ruido normal + un ataque masivo a la mitad
        y = np.random.normal(20, 2, 100)
        y[40:50] = y[40:50] * 5 # Pico de ataque
        sim_df = pd.DataFrame({'segundos': t, 'trafico_mbps': y})
        st.download_button("Descargar Archivo de Prueba", sim_df.to_csv(index=False), "test_network.csv")
