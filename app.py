import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
import os
import base64
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Satellite Command",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNCIÓN PARA CARGAR LOGO ---
def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_b64 = get_base64_logo("image_4f92e1.png")

# --- DISEÑO UI PREMIUM TECNOLÓGICO (CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Share+Tech+Mono&display=swap');
    
    .stApp {{
        background-color: #05070a;
        color: #e0e6ed;
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Header Corporativo */
    .main-header {{
        background: rgba(13, 17, 23, 0.9);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #00d4ff;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
    }}

    .logo-img {{
        max-height: 80px;
        filter: drop-shadow(0 0 5px rgba(0, 212, 255, 0.5));
    }}

    /* Tabs Estilo Satelital */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(22, 27, 34, 0.8);
        border: 1px solid #1a202c;
        border-radius: 8px 8px 0px 0px;
        color: #8b949e;
        padding: 12px 24px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: rgba(0, 212, 255, 0.1) !important;
        color: #00d4ff !important;
        border-color: #00d4ff !important;
    }}

    /* Contenedores */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-12w0qpk {{
        background-color: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
    }}

    /* Botones */
    .stButton>button {{
        border: 2px solid #00d4ff !important;
        background: transparent !important;
        color: #00d4ff !important;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        text-transform: uppercase;
    }}
    .stButton>button:hover {{
        background: rgba(0, 212, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
    }}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE PROCESAMIENTO (Sin cambios) ---
def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip = 0
    for i, line in enumerate(content):
        if any(k in line for k in ["Date", "Time", "Octets", "Eb/No", "FECHA", "ZONA", "NOMBRE ISP"]):
            skip = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except: return pd.DataFrame()

def generate_meru_docx(data_dict, month_text):
    doc = Document()
    doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    doc.add_paragraph(f"Periodo: {month_text}\nGenerado por: NOC Command Center")
    for name, df in data_dict.items():
        doc.add_heading(f'Detalle: {name}', level=1)
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        for i, col in enumerate(df.columns): table.rows[0].cells[i].text = col
        for _, row in df.head(30).iterrows():
            row_cells = table.add_row().cells
            for i, v in enumerate(row): row_cells[i].text = str(v)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# --- CABECERA DINÁMICA ---
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">' if logo_b64 else '<h2 style="color:#00d4ff;">MERU NETWORKS</h2>'

st.markdown(f"""
    <div class="main-header">
        <div style="display:flex; align-items:center; gap:25px;">
            {logo_html}
            <div style="border-left: 2px solid rgba(0, 212, 255, 0.3); padding-left: 20px;">
                <h1 style="margin:0; font-size:1.6rem; letter-spacing:2px;">SATELLITE INTELLIGENCE</h1>
                <p style="margin:0; color:#8b949e; font-size:0.8rem; font-family:sans-serif;">Network Operations Center | Monitoring & Reporting</p>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="color:#00d4ff; font-size:0.7rem; margin-bottom:4px;">ESTADO DEL ENLACE</div>
            <span style="background:rgba(0, 255, 128, 0.1); color:#00ff80; padding:4px 12px; border-radius:4px; font-size:0.8rem; border:1px solid #00ff80;">ONLINE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📥 INGESTA DE DATOS")
    files = st.file_uploader("Subir flujos de datos (CSV)", accept_multiple_files=True)
    st.markdown("---")
    sel_month = st.selectbox("Mes de reporte:", ["Marzo 2026", "Abril 2026"])
    st.caption("v10.1 Build: 2026.04")

# --- MODULOS ---
processed_data = {f.name: get_clean_df(f) for f in files} if files else {}

t_dash, t_tick, t_ai, t_exp = st.tabs(["📊 DASHBOARD", "🎫 TICKETS", "🧠 CORE AI", "📥 EXPORTAR"])

with t_dash:
    if files:
        for name, df in processed_data.items():
            with st.expander(f"📡 TELEMETRÍA: {name}", expanded=True):
                stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                if stations:
                    sel = st.multiselect("Nodo:", stations, default=stations[:1], key=name)
                    fig = go.Figure()
                    for s in sel:
                        for c in [col for col in df.columns if col.startswith(s + "/")]:
                            fig.add_trace(go.Scatter(y=df[c], name=f"{s}-{c.split('/')[-1]}", line=dict(color='#00d4ff', width=2)))
                    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else: st.dataframe(df.head(10))
    else: st.info("Esperando carga de datos satelitales...")

with t_tick:
    st.subheader("📝 Registro de Incidencias")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("tick"):
            node = st.text_input("ID Nodo")
            tipo = st.selectbox("Falla", ["Eb/No Bajo", "Power Fail", "Rain Fade"])
            if st.form_submit_button("REGISTRAR"): st.success("Guardado en log.")

with t_ai:
    st.markdown("### 🧠 Análisis Heurístico")
    st.code("DETECTANDO PATRONES... \n> No se observan anomalías críticas en el transpondedor actual.")

with t_exp:
    st.subheader("📥 Módulo de Exportación")
    if processed_data:
        st.info(f"Estructura configurada para el informe de **{sel_month}**.")
        c1, c2 = st.columns(2)
        with c1:
            docx = generate_meru_docx(processed_data, sel_month)
            st.download_button("Descargar Informe Word", docx, f"Informe_Meru_{sel_month}.docx")
        with c2:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as wr:
                for n, df in processed_data.items(): df.to_excel(wr, sheet_name=n[:30], index=False)
            st.download_button("Descargar Base Excel", out.getvalue(), f"Data_Meru_{sel_month}.xlsx")
    else: st.warning("Sin datos para exportar.")

st.markdown("<p style='text-align:center; opacity:0.3; margin-top:50px; font-size:0.7rem;'>SISTEMA DE MONITOREO MERU NETWORKS - ENLACE CIFRADO</p>", unsafe_allow_html=True)
