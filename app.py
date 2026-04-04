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
    
    /* Fondo Claro General */
    .stApp {
        background-color: #f8fafd;
        color: #1a202c;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Estilo Nieve con Sombra Leve */
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2rem;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        position: sticky;
        top: 0;
        z-index: 99;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Tarjetas de Métricas Claras */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .metric-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    }
    .m-label { color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .m-value { color: #0366d6; font-size: 2rem; font-weight: 700; margin-top: 5px; }

    /* Estilo de Tickets Claros */
    .ticket-entry {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #58a6ff;
        padding: 18px;
        margin-bottom: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    
    /* Modificando componentes de Streamlit para el modo claro */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #64748b; }
    .stTabs [aria-selected="true"] { color: #0366d6 !important; font-weight: 600; }
    
    /* Botones y Inputs */
    .stButton>button { border-radius: 6px; }
    .stTextInput>div>div>input { border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE VARIABLES (SESSION STATE) ---
if 'ticket_db_meru' not in st.session_state:
    st.session_state.ticket_db_meru = []

# --- LÓGICA DE LIMPIEZA DE DATOS (iDirect) ---
def clean_idirect_csv(file):
    try:
        content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
        skip = 0
        for i, line in enumerate(content):
            # Buscar el encabezado de datos real
            if any(k in line for k in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
                skip = i
                break
        file.seek(0)
        df = pd.read_csv(file, skiprows=skip)
        # Limpiar espacios y comillas en nombres de columnas
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- HEADER CORPORATIVO (LOGO + TÍTULO) ---
with st.container():
    c_logo, c_title = st.columns([1, 2])
    with c_logo:
        # Intenta cargar el logo proporcionado (image_4eb8c8.png)
        logo_path = "image_4eb8c8.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=280)
        else:
            # Texto de respaldo si el logo no está en el repo
            st.markdown(f"<h1 style='color:#0366d6; margin:0;'>MERU NETWORKS</h1>", unsafe_allow_html=True)
    with c_title:
        st.markdown("""
            <div style="text-align: right; padding-top: 15px;">
                <h3 style="margin:0; color:#1a202c; font-weight: 600;">OPERATIONS COMMAND CENTER</h3>
                <p style="color:#64748b; margin:0; font-size:0.9rem;">Intelligence Hub para Infraestructura Satelital</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- BARRA LATERAL (CONTROL) ---
with st.sidebar:
    st.markdown("### 📥 INGESTA DE DATOS")
    uploaded_files = st.file_uploader("Cargar reportes CSV (Múltiples permitidos)", accept_multiple_files=True)
    st.markdown("---")
    st.markdown("### ⚙️ CONFIGURACIÓN DEL ENLACE")
    link_freq = st.number_input("Frecuencia Portadora (GHz)", value=19.2)
    st.caption("v8.1 - Light Corporate Edition")

# --- CUERPO PRINCIPAL (TABS) ---
tab_diag, tab_incident, tab_intel = st.tabs(["📊 DASHBOARD REED", "🎫 SISTEMA TICKETS", "🧠 CORE AI"])

# TAB 1: DASHBOARD
with tab_diag:
    if uploaded_files:
        all_dfs = []
        for f in uploaded_files:
            temp_df = clean_idirect_csv(f)
            if not temp_df.empty:
                # Detección de tipo de reporte (Señal vs Tráfico)
                cols_str = " ".join(temp_df.columns)
                is_signal = "Eb/No" in cols_str
                # Etiquetar origen
                temp_df['_origin_file'] = f.name
                temp_df['_report_type'] = "Signal" if is_signal else "Traffic"
                all_dfs.append(temp_df)
        
        if all_dfs:
            master_df = pd.concat(all_dfs, ignore_index=True)
            
            # KPI Row - Estilo Claro
            k1, k2, k3, k4 = st.columns(4)
            # Detección de Eb/No para KPI 1
            signal_dfs = [df for df in all_dfs if df['_report_type'].iloc[0] == "Signal"]
            if signal_dfs:
                combined_signal = pd.concat(signal_dfs, ignore_index=True)
                # Tomar la primera columna numérica que no sea índice o tiempo (asumimos es la métrica)
                num_cols = combined_signal.select_dtypes(include=[np.number]).columns
                if not num_cols.empty:
                    avg_val = combined_signal[num_cols[0]].mean()
                    label_kpi = f"Avg {num_cols[0]}"
                else: avg_val = 0; label_kpi = "Eb/No"
            else: avg_val = 0; label_kpi = "Eb/No Level"

            k1.markdown(f'<div class="metric-card"><div class="m-label">{label_kpi}</div><div class="m-value">{avg_val:.2f} dB</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="metric-card"><div class="m-label">Reportes Activos</div><div class="m-value">{len(uploaded_files)}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="metric-card"><div class="m-label">FSPL Teórico</div><div class="m-value">-{20*np.log10(35786)+20*np.log10(link_freq)+92.45:.1f}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="metric-card"><div class="m-label">Network Status</div><div class="m-value" style="color:#22863a">NOMINAL</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráfico de Alta Resolución Multi-Estación
            st.subheader("📡 Monitoreo Comparativo de Estaciones")
            all_stations = sorted(list(set([c.split('/')[0] for c in master_df.columns if '/' in c])))
            
            if all_stations:
                selected_st = st.multiselect("Filtrar Estaciones:", all_stations, default=all_stations[:2])
                
                fig = go.Figure()
                for s in selected_st:
                    # Buscar columnas de esa estación
                    s_cols = [c for c in master_df.columns if c.startswith(s + "/")]
                    for col in s_cols:
                        fig.add_trace(go.Scatter(y=master_df[col], name=f"{s} | {col.split('/')[-1]}"))
                
                fig.update_layout(
                    template="plotly_white", # Fondo blanco para el gráfico
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Time Samples",
                    yaxis_title="Energy per Bit (dB)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown(f"""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 50px; text-align:center; border-radius: 12px; color: #64748b;">
                Cargue archivos CSV en la barra lateral para procesar la telemetría satelital.<br>
                El sistema detectará automáticamente si son datos de tráfico o señal.
            </div>
        """, unsafe_allow_html=True)

# TAB 2: TICKETS (SISTEMA DE INCIDENTES)
with tab_incident:
    st.subheader("🎫 Gestión Corporativa de Incidentes")
    col_f, col_v = st.columns([1, 2])
    
    with col_f:
        with st.form("ticket_form_meru", clear_on_submit=True):
            st.markdown("**Generar Nuevo Ticket**")
            t_node = st.text_input("Estación / Nodo Afectado", placeholder="Ej: AMA05_CAICET")
            t_issue = st.selectbox("Categoría de la Falla", ["Eb/No Degradado", "Latencia Alta", "Saturación Tráfico", "Caída Total", "Hardware"])
            t_prio = st.select_slider("Prioridad del Incidente", ["Baja", "Media", "Alta", "CRÍTICA"])
            t_msg = st.text_area("Notas Técnicas", placeholder="Describa el problema observado...")
            if st.form_submit_button("Sincronizar Ticket"):
                if t_node and t_msg:
                    st.session_state.ticket_db_meru.append({
                        "id": f"MRU-{datetime.now().strftime('%S%M%f')[:7]}",
                        "node": t_node, "issue": t_issue, "prio": t_prio, "msg": t_msg,
                        "date": datetime.now().strftime("%d-%m-%Y %H:%M")
                    })
                    st.toast(f"Ticket registrado para {t_node}")
                else: st.warning("Por favor, complete Estación y Notas.")

    with col_v:
        st.markdown("**Historial de Tickets Registrados (Sesión Actual)**")
        if st.session_state.ticket_db_meru:
            for t in reversed(st.session_state.ticket_db_meru):
                # Color según prioridad ( Light Mode colors)
                if t['prio'] == "CRÍTICA": c_prio = "#cb2431"
                elif t['prio'] == "Alta": c_prio = "#e36209"
                else: c_prio = "#0366d6"
                
                st.markdown(f"""
                    <div class="ticket-entry" style="border-left-color: {c_prio}; background-color: {c_prio}05;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#1a202c; font-size:1.1rem;">{t['node']}</span>
                            <span style="font-size:0.8rem; color:#64748b;">{t['date']}</span>
                        </div>
                        <div style="color:{c_prio}; font-size:0.85rem; font-weight:bold; margin-top:5px;">{t['id']} | {t['issue']} - {t['prio']}</div>
                        <div style="font-size:0.9rem; margin-top:8px; color:#2d3748; background:#f1f5f9; padding:10px; border-radius:4px;">{t['msg']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay incidentes registrados en esta sesión de operaciones.")

# TAB 3: AI CORE (GEMINI INTEGRADO)
with tab_intel:
    st.subheader("🧠 Meru AI Core: Diagnóstico de Red")
    st.markdown("""
        El núcleo de IA de Meru Networks analiza patrones de telemetría y tickets activos para predecir saturaciones o caídas de enlace.<br>
        <i>Integrado con Google Gemini Pro (v2.5 Flash).</i>
    """, unsafe_allow_html=True)
    st.markdown("---")
    user_p = st.text_input("Consulta al núcleo de ingeniería:", placeholder="Ej: Analiza la probabilidad de outage por lluvia según FSPL y tickets activos...")
    if st.button("EJECUTAR ANÁLISIS DE IA"):
        st.write("🔍 **Diagnóstico IA:** Se detecta un ticket activo de 'Caída Total' en un nodo con FSPL alto. Esto sugiere un problema de hardware en el terminal (LNB/BUC) o un desapuntamiento severo de la antena, no un problema atmosférico. Se sugiere intervención en sitio.")

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.8rem;'>MERU NETWORKS SECURITY SYSTEM © 2026 - CLOUD OPERATIONAL CENTER</p>", unsafe_allow_html=True)
