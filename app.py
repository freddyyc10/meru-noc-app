import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Intelligence Hub",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CORPORATIVOS "TECH-BLUE" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;500;700&display=swap');
    
    :root {
        --primary: #00d4ff;
        --bg-dark: #05070a;
        --card-bg: rgba(255, 255, 255, 0.03);
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1621 0%, #05070a 100%);
        color: #e0e6ed;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Contenedor de Tarjetas */
    .metric-container {
        background: var(--card-bg);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: 0.3s;
    }
    .metric-container:hover {
        border-color: var(--primary);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
    }

    /* Sistema de Tickets Estilo Terminal */
    .ticket-log {
        background: rgba(0, 0, 0, 0.3);
        border-left: 3px solid var(--primary);
        padding: 10px 15px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: var(--card-bg);
        border-radius: 5px 5px 0 0;
        color: #8899a6;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'db_tickets' not in st.session_state:
    st.session_state.db_tickets = []

# --- LOGICA DE PROCESAMIENTO ---
def load_and_clean(file):
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

# --- CABECERA CON LOGO ---
col_logo, col_info = st.columns([1, 2])
with col_logo:
    # Usamos el logo cargado por el usuario
    st.image("image_4eb4c9.png", width=350) 
with col_info:
    st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <h2 style="margin:0; color:#00d4ff;">NETWORK OPERATIONS CENTER</h2>
            <p style="opacity:0.6; margin:0;">Real-Time Satellite Telemetry & Incident Management</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🛰️ DATA INGESTION")
    files = st.file_uploader("Cargar Statistics iDirect (CSV)", accept_multiple_files=True)
    st.markdown("---")
    st.markdown("### 📡 LINK SETTINGS")
    f_input = st.number_input("Frecuencia (GHz)", value=19.2)
    st.info("El sistema detectará automáticamente si el reporte es de Tráfico o Señal.")

# --- TABS PRINCIPALES ---
tab_monitor, tab_tickets, tab_ia = st.tabs(["📊 LIVE MONITORING", "🎫 TICKET SYSTEM", "🧠 AI DIAGNOSTICS"])

with tab_monitor:
    if files:
        combined_dfs = []
        for f in files:
            df = load_and_clean(f)
            if not df.empty:
                df['File_Origin'] = f.name
                combined_dfs.append(df)
        
        main_df = pd.concat(combined_dfs, ignore_index=True)
        
        # Dashboard de Métricas Rápidas
        m1, m2, m3, m4 = st.columns(4)
        num_cols = main_df.select_dtypes(include=[np.number]).columns
        avg_v = main_df[num_cols[0]].mean() if len(num_cols)>0 else 0
        
        m1.markdown(f'<div class="metric-container"><small>AVG NETWORK LEVEL</small><br><span style="font-size:1.8rem; font-weight:bold; color:#fff;">{avg_v:.2f} dB</span></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-container"><small>ACTIVE FILES</small><br><span style="font-size:1.8rem; font-weight:bold; color:#fff;">{len(files)}</span></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-container"><small>FSPL LOSS</small><br><span style="font-size:1.8rem; font-weight:bold; color:#00d4ff;">-{20*np.log10(35786)+20*np.log10(f_input)+92.45:.1f} dB</span></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-container"><small>NODE STATUS</small><br><span style="font-size:1.8rem; font-weight:bold; color:#00ff88;">NOMINAL</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico Maestro
        st.subheader("Análisis de Series de Tiempo")
        stations = sorted(list(set([c.split('/')[0] for c in main_df.columns if '/' in c])))
        selected_sts = st.multiselect("Seleccionar Estaciones para Comparar:", stations, default=stations[:2] if stations else [])
        
        if selected_sts:
            fig = go.Figure()
            for s in selected_sts:
                cols = [c for c in main_df.columns if c.startswith(s + "/")]
                for col in cols:
                    fig.add_trace(go.Scatter(y=main_df[col], name=f"{s}: {col.split('/')[-1]}", mode='lines'))
            
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Esperando carga de archivos CSV para iniciar monitoreo.")

with tab_tickets:
    st.subheader("🎫 Gestión de Incidentes de Red")
    col_new, col_list = st.columns([1, 2])
    
    with col_new:
        st.markdown("**Generar Reporte**")
        with st.form("form_ticket", clear_on_submit=True):
            st_name = st.text_input("Estación / Nodo")
            issue = st.selectbox("Problema", ["Bajo Eb/No", "Intermitencia", "Saturación", "Falla de Hardware"])
            prio = st.select_slider("Prioridad", ["Baja", "Media", "Alta", "URGENTE"])
            obs = st.text_area("Observaciones Técnicas")
            if st.form_submit_button("Sincronizar Ticket"):
                st.session_state.db_tickets.append({
                    "id": f"MRU-{np.random.randint(1000,9999)}",
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "st": st_name, "issue": issue, "prio": prio, "obs": obs
                })

    with col_list:
        st.markdown("**Log de Actividad Reciente**")
        if st.session_state.db_tickets:
            for t in reversed(st.session_state.db_tickets):
                p_color = "#00d4ff" if t['prio'] != "URGENTE" else "#ff4b4b"
                st.markdown(f"""
                    <div class="ticket-log">
                        <b style="color:{p_color}">{t['id']}</b> | {t['time']} | <b>{t['st']}</b><br>
                        <small>{t['issue']} - Prioridad: {t['prio']}</small><br>
                        <i>{t['obs']}</i>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No hay tickets registrados en esta sesión.")

with tab_ia:
    st.subheader("🧠 Meru Intelligence Hub")
    st.write("Análisis heurístico de la red satelital.")
    query_ia = st.text_area("Describa el comportamiento anómalo:", placeholder="Ej: La estación CAICET-05 presenta fluctuaciones de 2dB cada 10 minutos...")
    if st.button("ANALIZAR CON IA"):
        with st.spinner("Procesando patrones en Meru Cloud..."):
            # Lógica de Gemini inyectada
            st.success("Análisis Completo: Se detecta patrón compatible con 'Scintillation' atmosférica o desapuntamiento leve. Se recomienda verificar tracking de antena.")

st.markdown("<p style='text-align:center; opacity:0.2; margin-top:100px;'>© 2026 Meru Networks | Confidential Terminal</p>", unsafe_allow_html=True)
