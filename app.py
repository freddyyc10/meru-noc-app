import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import time

# --- CONFIGURACIÓN DE IA ---
# Es mejor usar st.secrets o variables de entorno para la API_KEY
API_KEY = st.sidebar.text_input("Gemini API Key", type="password") 
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction="Eres el núcleo de inteligencia de Meru Networks. Analiza telemetría satelital Eb/No y detecta anomalías. Responde de forma concisa y técnica."
    )

def query_intelligence_hub(prompt):
    if not API_KEY:
        return "Por favor, introduce la API Key en la barra lateral."
    try:
        # El SDK de Google ya maneja gran parte del retry logic
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en el Centro de Inteligencia: {str(e)}"

# --- UI CONFIG ---
st.set_page_config(page_title="Meru Satellite Hub", layout="wide", page_icon="🛰️")

# Estilos mejorados: Gradientes y animaciones sutiles
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    .status-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .metric-val { 
        font-size: 28px; 
        font-weight: 800; 
        color: #58a6ff; 
        font-family: 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ Meru Networks | Intelligence Core")
st.markdown("---")

# --- GENERACIÓN DE DATOS (Realismo mejorado) ---
@st.cache_data
def get_telemetry_data():
    base = 9.39
    # Simulamos ruido gaussiano + una pequeña caída por desvanecimiento (fading)
    noise = np.random.normal(0, 0.2, 100)
    trend = np.linspace(0, -0.5, 100) # Simula una degradación ligera
    data = base + noise + trend
    return pd.DataFrame({"EbNo": data})

df = get_telemetry_data()
current_val = df['EbNo'].iloc[-1]

# --- DASHBOARD LAYOUT ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="status-card">LIVE EB/NO<br><span class="metric-val">{current_val:.2f} dB</span></div>', unsafe_allow_html=True)
with c2:
    status_color = "#00ff88" if current_val > 8.0 else "#ffcc00"
    st.markdown(f'<div class="status-card">LINK STATUS<br><span class="metric-val" style="color:{status_color};">STABLE</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="status-card">GATEWAY<br><span class="metric-val">CAICET-05</span></div>', unsafe_allow_html=True)

# --- CHART ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    y=df['EbNo'], 
    mode='lines+markers', 
    line=dict(color='#58a6ff', width=2),
    marker=dict(size=4),
    fill='tozeroy',
    fillcolor='rgba(88, 166, 255, 0.1)',
    name="Eb/No"
))

fig.update_layout(
    template="plotly_dark",
    height=400,
    hovermode="x unified",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(gridcolor='#30363d', title="Energy per Bit (dB)"),
    xaxis=dict(gridcolor='#30363d', title="Samples")
)
st.plotly_chart(fig, use_container_width=True)

# --- AI ANALYZER ---
with st.container():
    st.subheader("🧠 Intelligence Terminal")
    col_input, col_btn = st.columns([4, 1])
    
    with col_input:
        user_input = st.text_input("Consultar al núcleo:", placeholder="Ej: Analiza la probabilidad de Outage con este Eb/No")
    
    with col_btn:
        st.write(" ") # Espaciador
        analyze_clicked = st.button("EJECUTAR ANÁLISIS", use_container_width=True)

    if analyze_clicked:
        if user_input:
            with st.status("Procesando telemetría...", expanded=True) as status:
                prompt = f"Datos actuales: {df['EbNo'].iloc[-10:].tolist()}. Promedio: {df['EbNo'].mean()}. Pregunta: {user_input}"
                res = query_intelligence_hub(prompt)
                st.write(res)
                status.update(label="Análisis Completo", state="complete")
        else:
            st.toast("⚠️ Ingresa una consulta")
