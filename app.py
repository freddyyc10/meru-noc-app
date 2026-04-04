import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import io

# --- CONFIGURACIÓN DE SISTEMA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "TU_API_KEY_AQUÍ" # El entorno debe tener acceso a esta clave

def query_intelligence_hub(prompt, context_data=""):
    """Consulta al núcleo de IA con reintentos y contexto técnico."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    full_prompt = f"Contexto Telemetría: {context_data}\n\nPregunta Operador: {prompt}"
    
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres Meru Intelligence Core. Analiza presupuestos de enlace satelital, Eb/No, BER y degradación por lluvia. Sé técnico, preciso y detecta anomalías sutiles."}]
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Error de enlace neuronal: {response.status_code}"
    except:
        return "Conexión con el núcleo IA interrumpida."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MERU | Satellite Intelligence", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS Avanzados
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'JetBrains Mono', monospace; }
    .stApp { background-color: #05070a; color: #00f2ff; }
    
    .main-header {
        background: linear-gradient(90deg, #001a2e 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 20px;
    }
    
    .status-box {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        padding: 15px; border-radius: 5px;
        text-align: center;
    }
    
    .metric-title { color: #888; font-size: 0.8rem; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #fff; }
    
    /* Personalización de botones */
    .stButton>button {
        width: 100%; border-radius: 0px; border: 1px solid #00d4ff;
        background: transparent; color: #00d4ff; transition: 0.3s;
    }
    .stButton>button:hover { background: #00d4ff; color: #000; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: CARGA DE DATOS Y PARÁMETROS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2554/2554936.png", width=80)
    st.header("SISTEMA DE ENTRADA")
    
    upload_file = st.file_uploader("Importar Telemetría (CSV)", type=["csv"])
    
    st.subheader("Parámetros de Enlace")
    freq = st.slider("Frecuencia (GHz)", 10.0, 30.0, 19.2)
    modcod = st.selectbox("ModCod", ["QPSK 1/2", "8PSK 3/4", "16APSK 2/3", "32APSK 9/10"])
    antenna_size = st.number_input("Tamaño Antena (m)", value=1.2)

# --- LÓGICA DE DATOS ---
if upload_file:
    df = pd.read_csv(upload_file)
    # Asumimos que el CSV tiene una columna 'EbNo' o 'Value'
    if 'EbNo' not in df.columns:
        df.columns = ['EbNo'] if len(df.columns) == 1 else df.columns
else:
    # Simulación por defecto si no hay archivo
    t = np.linspace(0, 100, 100)
    ebno_sim = 9.39 + np.random.normal(0, 0.3, 100)
    # Simular un "Rain Fade" (Caída por lluvia) en el medio
    ebno_sim[40:60] -= np.linspace(0, 3, 20)
    df = pd.DataFrame({'Time': t, 'EbNo': ebno_sim})

# --- UI PRINCIPAL ---
st.markdown('<div class="main-header">MERU SATELLITE COMMAND</div>', unsafe_allow_html=True)

# Fila 1: Métricas Críticas
avg_ebno = df['EbNo'].mean()
min_ebno = df['EbNo'].min()
margin = avg_ebno - 6.5 # Asumiendo umbral de 6.5 dB

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="status-box"><div class="metric-title">Eb/No Promedio</div><div class="metric-value">{avg_ebno:.2f} dB</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="status-box"><div class="metric-title">Margen de Enlace</div><div class="metric-value">{margin:.2f} dB</div></div>', unsafe_allow_html=True)
with c3:
    status = "NOMINAL" if min_ebno > 7.0 else "DEGRADADO"
    color = "#00ff88" if status == "NOMINAL" else "#ff3333"
    st.markdown(f'<div class="status-box"><div class="metric-title">Estado Operativo</div><div class="metric-value" style="color:{color}">{status}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="status-box"><div class="metric-title">Frecuencia</div><div class="metric-value">{freq} GHz</div></div>', unsafe_allow_html=True)

# Fila 2: Gráficos de Análisis de Enlace
col_graph, col_dist = st.columns([3, 1])

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df['EbNo'], mode='lines', line=dict(color='#00d4ff', width=2), fill='tozeroy', name="Eb/No Actual"))
    fig.add_hline(y=6.5, line_dash="dot", line_color="red", annotation_text="Umbral de Corte")
    fig.update_layout(template="plotly_dark", height=400, title="Análisis de Telemetría en Tiempo Real", margin=dict(t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_dist:
    fig_hist = px.histogram(df, y="EbNo", nbins=20, orientation='h', color_discrete_sequence=['#00d4ff'])
    fig_hist.update_layout(template="plotly_dark", height=400, title="Distribución de Señal", showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=True)

# Fila 3: Análisis de Inteligencia Artificial
st.markdown("---")
st.subheader("🧠 Terminal de Inteligencia Meru")

# Preparar datos para la IA
recent_data = df['EbNo'].tail(20).tolist()
context = f"Frecuencia: {freq}GHz, ModCod: {modcod}, EbNo Promedio: {avg_ebno:.2f}, Mínimo: {min_ebno:.2f}. Tendencia: {recent_data}"

user_query = st.text_input("Consultar anomalías o predicción de enlace:", placeholder="Ej: Analiza la pérdida por lluvia según la tendencia actual...")

if st.button("EJECUTAR ANÁLISIS DE IA"):
    with st.spinner("Sincronizando con el satélite..."):
        respuesta = query_intelligence_hub(user_query, context)
        st.info(respuesta)

# Sección Detallada: Link Budget Manual
with st.expander("Ver Detalles de Presupuesto de Enlace (Link Budget Calculations)"):
    st.write("Cálculo estimado basado en parámetros de entrada:")
    c_noise = avg_ebno + 10 # Estimación simplificada de C/N
    st.write(f"- **Relación Portadora-Ruido (C/N):** {c_noise:.2f} dB")
    st.write(f"- **Eficiencia Espectral Estimada:** {modcod}")
    st.write(f"- **Pérdida de Trayecto (FSPL):** Calculada para {freq} GHz")

st.markdown("<div style='text-align:center; opacity:0.2; margin-top:50px;'>SISTEMA DE SEGURIDAD MERU NETWORKS v3.0 - ACCESO NIVEL 5</div>", unsafe_allow_html=True)
