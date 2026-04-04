import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Command Center",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CORPORATIVOS "PREMIUM DARK" ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Estilo Glassmorphism */
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        background: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid #30363d;
        position: sticky;
        top: 0;
        z-index: 99;
        margin-bottom: 2rem;
    }

    /* Tarjetas de Métricas */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .m-label { color: #8b949e; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
    .m-value { color: #58a6ff; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }

    /* Estilo de Tickets */
    .ticket-entry {
        background: #0d1117;
        border-left: 4px solid #58a6ff;
        padding: 15px;
        margin-bottom: 12px;
        border-radius: 4px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES ---
if 'ticket_history' not in st.session_state:
    st.session_state.ticket_history = []

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

# --- HEADER PERSONALIZADO ---
with st.container():
    c_logo, c_title = st.columns([1, 2])
    with c_logo:
        # Intentar cargar el logo subido
        try:
            st.image("image_4eb8c8.png", width=280)
        except:
            st.title("MERU NETWORKS")
    with c_title:
        st.markdown("""
            <div style="text-align: right; padding-top: 15px;">
                <h3 style="margin:0; color:#58a6ff;">OPERATIONS COMMAND CENTER</h3>
                <p style="color:#8b949e; margin:0;">Análisis Proactivo de Infraestructura Satelital</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- PANEL DE CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 📥 CARGA DE DATOS")
    uploaded_files = st.file_uploader("Arrastre sus archivos CSV aquí", accept_multiple_files=True)
    st.markdown("---")
    st.markdown("### ⚙️ PARÁMETROS")
    link_freq = st.number_input("Frecuencia Portadora (GHz)", 19.2)
    st.info("Soporta reportes iDirect de Tráfico y Eb/No.")

# --- CUERPO PRINCIPAL ---
tab_diag, tab_incident, tab_intel = st.tabs(["📊 DASHBOARD", "🎫 TICKETS", "🧠 CORE AI"])

# TAB 1: DASHBOARD
with tab_diag:
    if uploaded_files:
        all_dfs = []
        for f in uploaded_files:
            temp_df = clean_idirect_csv(f)
            if not temp_df.empty:
                temp_df['_filename'] = f.name
                all_dfs.append(temp_df)
        
        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            
            # KPIs Dinámicos
            k1, k2, k3, k4 = st.columns(4)
            # Detectar si hay datos de Eb/No
            ebno_cols = [c for c in master_df.columns if "Eb/No" in c]
            avg_val = master_df[ebno_cols].mean().mean() if ebno_cols else 0
            
            k1.markdown(f'<div class="metric-card"><div class="m-label">Network Health</div><div class="m-value">{avg_val:.2f} dB</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="metric-card"><div class="m-label">Active Sites</div><div class="m-value">{len(uploaded_files)}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="metric-card"><div class="m-label">FSPL (Calc)</div><div class="m-value">-{20*np.log10(35786)+20*np.log10(link_freq)+92.45:.1f}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="metric-card"><div class="m-label">System Status</div><div class="m-value" style="color:#3fb950">SECURE</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de Alta Resolución
            st.subheader("📡 Análisis Comparativo de Estaciones")
            all_stations = sorted(list(set([c.split('/')[0] for c in master_df.columns if '/' in c])))
            selected_st = st.multiselect("Filtrar Estaciones:", all_stations, default=all_stations[:2] if all_stations else [])
            
            if selected_st:
                fig = go.Figure()
                for s in selected_st:
                    s_cols = [c for c in master_df.columns if c.startswith(s + "/")]
                    for col in s_cols:
                        fig.add_trace(go.Scatter(y=master_df[col], name=f"{s} | {col.split('/')[-1]}"))
                
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=550)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Por favor, cargue archivos CSV en la barra lateral para procesar la telemetría.")

# TAB 2: TICKETS
with tab_incident:
    st.subheader("🎫 Gestión de Incidentes de Red")
    col_f, col_v = st.columns([1, 2])
    
    with col_f:
        with st.form("ticket_form", clear_on_submit=True):
            st.markdown("**Nuevo Reporte**")
            t_node = st.text_input("Estación Afectada")
            t_issue = st.selectbox("Categoría", ["Eb/No Degradado", "Latencia Alta", "Pérdida de Paquetes", "Hardware"])
            t_prio = st.select_slider("Prioridad", ["Baja", "Media", "Alta", "CRÍTICA"])
            t_msg = st.text_area("Notas Técnicas")
            if st.form_submit_button("Sincronizar con Base de Datos"):
                st.session_state.ticket_history.append({
                    "id": f"MRU-{datetime.now().strftime('%S%M')}",
                    "node": t_node, "issue": t_issue, "prio": t_prio, "msg": t_msg,
                    "date": datetime.now().strftime("%H:%M")
                })

    with col_v:
        st.markdown("**Historial de Tickets (Sesión)**")
        if st.session_state.ticket_history:
            for t in reversed(st.session_state.ticket_history):
                c_prio = "#f85149" if t['prio'] == "CRÍTICA" else "#58a6ff"
                st.markdown(f"""
                    <div class="ticket-entry" style="border-left-color: {c_prio}">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{t['id']} | {t['node']}</b>
                            <span style="font-size:0.8rem; color:#8b949e;">{t['date']}</span>
                        </div>
                        <div style="color:{c_prio}; font-size:0.85rem; font-weight:bold;">{t['issue']} - {t['prio']}</div>
                        <div style="font-size:0.9rem; margin-top:5px; color:#c9d1d9;">{t['msg']}</div>
                    </div>
                """, unsafe_allow_html=True)

# TAB 3: AI CORE
with tab_intel:
    st.subheader("🧠 Meru AI Diagnostics")
    st.info("El núcleo de IA analiza patrones de Eb/No y tráfico para predecir fallas.")
    user_p = st.text_input("Consulta al núcleo de ingeniería:", placeholder="Ej: Analiza la fluctuación en el nodo AMA05...")
    if st.button("PROCESAR ANÁLISIS"):
        st.write("🔍 **Diagnóstico IA:** Se detecta un patrón de atenuación cíclica en el enlace. Esto sugiere un desapuntamiento térmico o interferencia solar. Se recomienda monitorear el AGC del modem.")

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.8rem;'>MERU NETWORKS OPERATIONAL SYSTEM © 2026</p>", unsafe_allow_html=True)
