import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests

# --- CONFIGURACIÓN DE SISTEMA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "TU_API_KEY_AQUÍ" 

def query_intelligence_hub(prompt, context_data=""):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"{context_data}\n\nPregunta: {prompt}"}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres Meru Intelligence Core. Analiza telemetría satelital Eb/No. Sé técnico y breve."}]
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Error: No se pudo conectar con el núcleo de IA."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MERU | Satellite Intelligence", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #00f2ff; font-family: 'Courier New', monospace; }
    .status-box {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        padding: 15px; border-radius: 5px;
        text-align: center; margin-bottom: 10px;
    }
    .metric-value { font-size: 2rem; font-weight: bold; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS (CORREGIDA) ---
with st.sidebar:
    st.header("SISTEMA DE ENTRADA")
    upload_file = st.file_uploader("Importar Telemetría (CSV)", type=["csv"])
    freq = st.slider("Frecuencia (GHz)", 10.0, 30.0, 19.2)

if upload_file:
    df = pd.read_csv(upload_file)
    # Lógica para evitar el KeyError:
    if 'EbNo' not in df.columns:
        # Intentamos buscar cualquier columna que parezca numérica
        cols_numericas = df.select_dtypes(include=[np.number]).columns
        if len(cols_numericas) > 0:
            df = df.rename(columns={cols_numericas[0]: 'EbNo'})
        else:
            st.error("El CSV no tiene columnas numéricas detectables.")
            st.stop()
else:
    # Simulación si no hay archivo
    t = np.linspace(0, 100, 100)
    ebno_sim = 9.39 + np.random.normal(0, 0.3, 100)
    df = pd.DataFrame({'EbNo': ebno_sim})

# --- UI PRINCIPAL ---
st.title("🛰️ MERU SATELLITE COMMAND")

avg_ebno = df['EbNo'].mean()
min_ebno = df['EbNo'].min()
margin = avg_ebno - 6.5 

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="status-box">Eb/No Promedio<br><span class="metric-value">{avg_ebno:.2f} dB</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="status-box">Margen de Enlace<br><span class="metric-value">{margin:.2f} dB</span></div>', unsafe_allow_html=True)
with c3:
    status = "NOMINAL" if min_ebno > 7.0 else "CRÍTICO"
    color = "#00ff88" if status == "NOMINAL" else "#ff3333"
    st.markdown(f'<div class="status-box">Estado<br><span class="metric-value" style="color:{color}">{status}</span></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="status-box">Frecuencia<br><span class="metric-value">{freq} GHz</span></div>', unsafe_allow_html=True)

# Gráfico Principal
fig = go.Figure()
fig.add_trace(go.Scatter(y=df['EbNo'], mode='lines', line=dict(color='#00d4ff'), fill='tozeroy'))
fig.update_layout(template="plotly_dark", height=400, margin=dict(t=20, b=20))
st.plotly_chart(fig, use_container_width=True)

# Terminal de IA
st.subheader("🧠 Análisis Predictivo (IA)")
user_query = st.text_input("Pregunta al sistema:", placeholder="¿Hay riesgo de interrupción?")

if st.button("ANALIZAR"):
    context = f"Datos: EbNo promedio {avg_ebno:.2f}, Freq {freq}GHz."
    respuesta = query_intelligence_hub(user_query, context)
    st.info(respuesta)
