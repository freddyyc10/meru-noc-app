import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests

# --- CONFIGURACIÓN DE SISTEMA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "TU_API_KEY_AQUÍ" 

def query_intelligence_hub(prompt, telemetry_summary):
    """Consulta al núcleo de IA de Meru."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"DATOS TÉCNICOS: {telemetry_summary}\n\nPREGUNTA: {prompt}"}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres Meru Intelligence Core. Analiza telemetría satelital (Eb/No, BER, Rain Fade). Responde como un ingeniero experto, detectando anomalías y sugiriendo acciones correctivas."}]
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "⚠️ Error de comunicación con el satélite: Núcleo IA fuera de línea."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MERU NETWORKS | COMMAND CENTER", layout="wide")

# Estilos CSS de alto impacto
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #020508; color: #00f2ff; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00d4ff; text-align: center; font-size: 3rem; text-shadow: 0 0 20px #00d4ff; margin-bottom: 30px; }
    .st-emotion-cache-16idsys p { font-family: 'Courier New', monospace; }
    .metric-card {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        padding: 20px; border-radius: 10px;
        box-shadow: inset 0 0 10px rgba(0, 212, 255, 0.2);
        text-align: center;
    }
    .metric-val { font-size: 2.5rem; font-weight: bold; color: #ffffff; }
    .sidebar-text { font-size: 0.9rem; color: #888; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">MERU SATELLITE INTELLIGENCE</h1>', unsafe_allow_html=True)

# --- SIDEBAR: GESTIÓN DE ARCHIVOS ---
with st.sidebar:
    st.header("🛰️ DATA INGESTION")
    uploaded_files = st.file_uploader("Cargar Telemetría (Hasta 3 CSVs)", type=["csv"], accept_multiple_files=True)
    
    st.markdown("---")
    st.header("⚙️ LINK PARAMETERS")
    freq_ghz = st.number_input("Frecuencia (GHz)", value=19.2)
    antenna_gain = st.slider("Ganancia de Antena (dB)", 30, 60, 45)
    mod_scheme = st.selectbox("Esquema de Modulación", ["QPSK", "8PSK", "16APSK", "32APSK"])

# --- PROCESAMIENTO DE DATOS ---
all_dfs = []
if uploaded_files:
    for file in uploaded_files:
        temp_df = pd.read_csv(file)
        # Limpieza inteligente: buscar la columna numérica principal
        numeric_cols = temp_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            temp_df = temp_df.rename(columns={numeric_cols[0]: 'EbNo'})
            temp_df['Source'] = file.name
            all_dfs.append(temp_df)
    
    if all_dfs:
        main_df = pd.concat(all_dfs, ignore_index=True)
    else:
        st.error("No se encontraron datos numéricos en los archivos.")
        st.stop()
else:
    # Datos simulados de alta fidelidad si no hay archivos
    t = np.linspace(0, 50, 100)
    ebno_sim = 9.39 + np.random.normal(0, 0.4, 100)
    ebno_sim[30:45] -= 2.5  # Simular Rain Fade
    main_df = pd.DataFrame({'EbNo': ebno_sim, 'Source': 'Simulated_Link_01'})

# --- DASHBOARD DE MÉTRICAS ---
avg_val = main_df['EbNo'].mean()
max_val = main_df['EbNo'].max()
min_val = main_df['EbNo'].min()
stability = 100 - (main_df['EbNo'].std() * 10)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card">AVG Eb/No<br><span class="metric-val">{avg_val:.2f}</span><br>dB</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card">PEAK SIGNAL<br><span class="metric-val">{max_val:.2f}</span><br>dB</div>', unsafe_allow_html=True)
with col3:
    status_color = "#00ff88" if min_val > 7.5 else "#ff4444"
    st.markdown(f'<div class="metric-card">MIN VALUE<br><span class="metric-val" style="color:{status_color}">{min_val:.2f}</span><br>dB</div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card">STABILITY<br><span class="metric-val">{stability:.1f}%</span><br>Link Integrity</div>', unsafe_allow_html=True)

# --- VISUALIZACIÓN AVANZADA ---
st.markdown("### 📊 ANALISIS DE MULTI-ENLACE")
fig = px.line(main_df, y='EbNo', color='Source', title="Comparativa de Telemetría Satelital")
fig.add_hline(y=6.5, line_dash="dash", line_color="red", annotation_text="Link Outage Threshold")
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title="Time Samples",
    yaxis_title="Energy per Bit (dB)",
    font=dict(family="Courier New", color="#00f2ff")
)
st.plotly_chart(fig, use_container_width=True)

# --- MÓDULO DE IA ---
st.markdown("---")
col_ai, col_details = st.columns([2, 1])

with col_ai:
    st.subheader("🧠 MERU AI CORE: PREDICTIVE ANALYSIS")
    user_q = st.text_input("Consultar al sistema (Ej: 'Predice el BER basado en estos datos')", placeholder="Escribe tu consulta técnica...")
    
    if st.button("RUN NEURAL ANALYSIS"):
        with st.spinner("Analizando patrones de señal..."):
            summary = f"EbNo Promedio: {avg_val:.2f}, Min: {min_val:.2f}, Freq: {freq_ghz}GHz, Mod: {mod_scheme}."
            analysis = query_intelligence_hub(user_q, summary)
            st.info(analysis)

with col_details:
    st.subheader("📋 LINK BUDGET SPECS")
    st.write(f"**Carrier-to-Noise Ratio (C/N):** {avg_val + 1.2:.2f} dB")
    st.write(f"**Rain Margin:** {avg_val - 6.5:.2f} dB")
    st.write(f"**Effective Isotropic Radiated Power:** {antenna_gain + 10} dBW")
    
    if avg_val < 8.0:
        st.warning("⚠️ ALERTA: Margen de lluvia bajo. Se recomienda aumentar potencia de Uplink (AUPC).")

st.markdown("<br><p style='text-align:center; opacity:0.3;'>SECURED BY MERU NETWORKS | CLOUD ENGINE v3.5</p>", unsafe_allow_html=True)
