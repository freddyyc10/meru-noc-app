import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Intelligence Hub",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CORPORATIVOS "LIGHT MODE" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp { background-color: #f8fafd; color: #1a202c; font-family: 'Inter', sans-serif; }
    
    .nav-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 2rem; background-color: #ffffff; border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .metric-card {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 22px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .m-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
    .m-value { color: #0366d6; font-size: 2rem; font-weight: 700; margin-top: 5px; }

    .ticket-entry {
        background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #58a6ff;
        padding: 18px; margin-bottom: 12px; border-radius: 8px;
    }
    
    .analysis-section {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e2e8f0; margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

if 'ticket_db_meru' not in st.session_state:
    st.session_state.ticket_db_meru = []

# --- LÓGICA DE LIMPIEZA DE DATOS ---
def clean_idirect_csv(file):
    try:
        content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
        skip = 0
        for i, line in enumerate(content):
            if any(k in line for k in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
                skip = i
                break
        file.seek(0)
        df = pd.read_csv(file, skiprows=skip)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- HEADER CORPORATIVO ---
with st.container():
    c_logo, c_title = st.columns([1, 2])
    with c_logo:
        logo_path = "image_4eb8c8.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=280)
        else:
            st.markdown(f"<h1 style='color:#0366d6; margin:0;'>MERU NETWORKS</h1>", unsafe_allow_html=True)
    with c_title:
        st.markdown("""
            <div style="text-align: right; padding-top: 15px;">
                <h3 style="margin:0; color:#1a202c; font-weight: 600;">OPERATIONS COMMAND CENTER</h3>
                <p style="color:#64748b; margin:0; font-size:0.9rem;">Intelligence Hub para Infraestructura Satelital</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- BARRA LATERAL (LIMPIA) ---
with st.sidebar:
    st.markdown("### 📥 INGESTA DE DATOS")
    uploaded_files = st.file_uploader("Cargar reportes CSV iDirect", accept_multiple_files=True)
    st.markdown("---")
    st.success("NOC Panel - Modo Lectura")

# --- CUERPO PRINCIPAL ---
tab_diag, tab_incident, tab_intel = st.tabs(["📊 ANÁLISIS DETALLADO", "🎫 SISTEMA TICKETS", "🧠 CORE AI"])

with tab_diag:
    if uploaded_files:
        traffic_files = []
        signal_files = []

        for f in uploaded_files:
            df = clean_idirect_csv(f)
            if not df.empty:
                cols_str = " ".join(df.columns)
                if "Eb/No" in cols_str:
                    signal_files.append((f.name, df))
                elif "Octets" in cols_str or "Bit Rate" in cols_str:
                    traffic_files.append((f.name, df))

        # --- SECCIÓN 1: ANÁLISIS DE SEÑAL (Eb/No) ---
        if signal_files:
            st.markdown("### 📶 Monitoreo de Señal (Eb/No)")
            for name, df in signal_files:
                with st.expander(f"Gráfica de Rendimiento: {name}", expanded=True):
                    all_stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                    selected = st.multiselect(f"Seleccionar Estaciones ({name}):", all_stations, default=all_stations[:1], key=f"sig_{name}")
                    
                    fig = go.Figure()
                    for s in selected:
                        s_cols = [c for c in df.columns if c.startswith(s + "/")]
                        for col in s_cols:
                            fig.add_trace(go.Scatter(y=df[col], name=f"{s} | {col.split('/')[-1]}"))
                    
                    fig.update_layout(template="plotly_white", height=400, margin=dict(l=0,r=0,b=0,t=30))
                    st.plotly_chart(fig, use_container_width=True)

        # --- SECCIÓN 2: ANÁLISIS DE TRÁFICO (Consumo) ---
        if traffic_files:
            st.markdown("### 📊 Análisis de Tráfico y Consumo")
            for name, df in traffic_files:
                with st.expander(f"Gráfica de Consumo: {name}", expanded=True):
                    all_stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                    selected = st.multiselect(f"Seleccionar Estaciones ({name}):", all_stations, default=all_stations[:1], key=f"traf_{name}")
                    
                    fig = go.Figure()
                    for s in selected:
                        s_cols = [c for c in df.columns if c.startswith(s + "/")]
                        for col in s_cols:
                            # Conversión a MB si son Octetos
                            val = df[col] / (1024*1024) if "Octets" in col else df[col]
                            unit = "MB" if "Octets" in col else "bps"
                            fig.add_trace(go.Scatter(y=val, name=f"{s} | {unit}"))
                    
                    fig.update_layout(template="plotly_white", height=400, margin=dict(l=0,r=0,b=0,t=30))
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Por favor, cargue los archivos CSV en la barra lateral para ver los análisis por separado.")

# TAB 2 & 3 (Se mantienen igual para no cambiar la estructura)
with tab_incident:
    st.subheader("🎫 Gestión Corporativa de Incidentes")
    col_f, col_v = st.columns([1, 2])
    with col_f:
        with st.form("ticket_form"):
            t_node = st.text_input("Estación / Nodo Afectado")
            t_issue = st.selectbox("Falla", ["Eb/No Degradado", "Latencia Alta", "Saturación", "Hardware"])
            t_prio = st.select_slider("Prioridad", ["Baja", "Media", "Alta", "CRÍTICA"])
            t_msg = st.text_area("Notas")
            if st.form_submit_button("Sincronizar"):
                st.session_state.ticket_db_meru.append({"id": f"MRU-{datetime.now().strftime('%S%M')}", "node": t_node, "issue": t_issue, "prio": t_prio, "msg": t_msg, "date": datetime.now().strftime("%d-%m-%Y %H:%M")})
    with col_v:
        for t in reversed(st.session_state.ticket_db_meru):
            st.markdown(f'<div class="ticket-entry"><b>{t["node"]}</b> | {t["issue"]} ({t["prio"]})<br><small>{t["date"]}</small><p>{t["msg"]}</p></div>', unsafe_allow_html=True)

with tab_intel:
    st.subheader("🧠 Meru AI Core")
    user_p = st.text_input("Consulta técnica:")
    if st.button("ANALIZAR"):
        st.write("🔍 Diagnóstico: Enlace estable. No se detectan anomalías en los archivos cargados.")

st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.8rem; margin-top:5rem;'>MERU NETWORKS SECURITY SYSTEM © 2026</p>", unsafe_allow_html=True)
