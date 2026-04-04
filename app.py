import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Intelligence Hub",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DISEÑO UI PREMIUM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Fondo y tipografía base */
    .stApp {
        background-color: #f0f2f6;
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar estilizada */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Contenedores de Tarjetas (Cards) */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-12w0qpk {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Header Estilizado */
    .main-header {
        background: linear-gradient(90deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Tabs Personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0366d6 !important;
        color: white !important;
        border-color: #0366d6 !important;
    }

    /* Botones Premium */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #0366d6;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #024ea3;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS (Preservada) ---
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
    title = doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Periodo: {month_text}\nDepartamento: Operaciones de Red (NOC)")
    
    sections = {
        "FALLAS INTERNAS": "2. REPORTE DE FALLAS INTERNAS (GESTIÓN PROPIA)",
        "ISP": "3. REPORTE DE FALLAS DE PROVEEDORES (ISP)",
        "RECLAMOS": "4. ATENCIÓN DE RECLAMOS DEL ABONADO"
    }

    doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
    doc.add_paragraph("Resumen de disponibilidad y eventos críticos del mes.")

    for name, df in data_dict.items():
        heading = "DETALLE DE OPERACIONES"
        for key, val in sections.items():
            if key in name.upper(): heading = val
        
        doc.add_heading(heading, level=1)
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        for i, col in enumerate(df.columns):
            table.rows[0].cells[i].text = col
        for _, row in df.head(40).iterrows():
            row_cells = table.add_row().cells
            for i, v in enumerate(row): row_cells[i].text = str(v)
    
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# --- HEADER PREMIUM ---
with st.container():
    st.markdown(f"""
        <div class="main-header">
            <div>
                <h1 style="margin:0; color:#0366d6; font-size:1.8rem;">MERU NETWORKS</h1>
                <p style="margin:0; color:#64748b; font-size:0.9rem;">Intelligence Hub | NOC Operational Command</p>
            </div>
            <div style="text-align:right;">
                <span style="background:#e1effe; color:#0366d6; padding:5px 12px; border-radius:20px; font-size:0.8rem; font-weight:700;">
                    SISTEMA ACTIVO v9.2
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📥 CARGA DE DATOS")
    uploaded_files = st.file_uploader("Arrastre reportes CSV aquí", accept_multiple_files=True)
    st.markdown("---")
    st.markdown("### ⚙️ PARÁMETROS")
    sel_month = st.selectbox("Mes de reporte:", ["Marzo 2026", "Abril 2026", "Mayo 2026"])
    st.info("La IA analizará los datos cargados automáticamente.")

# --- CUERPO PRINCIPAL ---
processed_data = {}
if uploaded_files:
    for f in uploaded_files:
        processed_data[f.name] = get_clean_df(f)

tab_diag, tab_incident, tab_intel, tab_export = st.tabs([
    "📊 Dashboard Visual", 
    "🎫 Gestión de Tickets", 
    "🧠 Core IA", 
    "📥 Exportación"
])

# 1. DASHBOARD
with tab_diag:
    if uploaded_files:
        st.markdown("### Análisis de Telemetría Satelital")
        for name, df in processed_data.items():
            with st.container():
                st.markdown(f"**Archivo:** `{name}`")
                stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                if stations:
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        sel = st.multiselect(f"Filtrar Nodo:", stations, default=stations[:1], key=f"dash_{name}")
                    with c2:
                        fig = go.Figure()
                        for s in sel:
                            for c in [col for col in df.columns if col.startswith(s + "/")]:
                                fig.add_trace(go.Scatter(y=df[c], name=f"{s}-{c.split('/')[-1]}", line=dict(width=2)))
                        fig.update_layout(
                            template="plotly_white", 
                            height=300, 
                            margin=dict(l=10, r=10, t=10, b=10),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(df.head(5), use_container_width=True)
                st.markdown("---")
    else:
        st.info("👋 Bienvenido. Cargue archivos en la barra lateral para comenzar el análisis.")

# 2. TICKETS
with tab_incident:
    st.markdown("### Centro de Incidentes")
    col_f, col_v = st.columns([1, 2])
    with col_f:
        st.markdown('<div style="background:white; padding:20px; border-radius:12px; border:1px solid #e2e8f0;">', unsafe_allow_html=True)
        with st.form("t_form"):
            st.write("**Nuevo Reporte**")
            node = st.text_input("ID del Nodo / Estación")
            issue = st.selectbox("Categoría", ["Eb/No Degradado", "Falla de Hardware", "Corte de Energía", "Interferencia"])
            if st.form_submit_button("Registrar en Bitácora"):
                st.success(f"Ticket registrado para {node}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_v:
        st.markdown("**Incidentes Recientes**")
        st.markdown('<div class="ticket-entry"><b>NODO_DEMO_01</b> | Eb/No Degradado<br><small>Hace 5 minutos</small></div>', unsafe_allow_html=True)

# 3. CORE IA
with tab_intel:
    st.markdown("### Inteligencia Predictiva")
    st.markdown("""
    <div style="background:#f8fafc; padding:30px; border-radius:12px; border:2px dashed #cbd5e1; text-align:center;">
        <h2 style="color:#64748b;">🧠</h2>
        <p style="color:#64748b;">El motor de IA está procesando los datos para detectar patrones de Sun Outage o Rain Fade.</p>
    </div>
    """, unsafe_allow_html=True)

# 4. EXPORTAR (Mantenido según tus modelos)
with tab_export:
    st.markdown("### Generación de Informes Corporativos")
    if processed_data:
        st.write(f"Los documentos se generarán bajo la estructura oficial para: **{sel_month}**")
        c_w, c_e = st.columns(2)
        with c_w:
            st.markdown("""
                <div style="background:white; padding:20px; border-radius:12px; border:1px solid #e2e8f0;">
                    <h4>📄 Formato Word</h4>
                    <p style="font-size:0.8rem; color:#64748b;">Incluye Resumen Ejecutivo y tablas formateadas de Fallas e ISP.</p>
                </div>
            """, unsafe_allow_html=True)
            docx_data = generate_meru_docx(processed_data, sel_month)
            st.download_button("Descargar Informe .DOCX", docx_data, f"Informe_Meru_{sel_month}.docx")
        
        with c_e:
            st.markdown("""
                <div style="background:white; padding:20px; border-radius:12px; border:1px solid #e2e8f0;">
                    <h4>📊 Formato Excel</h4>
                    <p style="font-size:0.8rem; color:#64748b;">Consolidado de datos en pestañas independientes por reporte.</p>
                </div>
            """, unsafe_allow_html=True)
            output_x = io.BytesIO()
            with pd.ExcelWriter(output_x, engine='xlsxwriter') as writer:
                for n, df in processed_data.items():
                    df.to_excel(writer, sheet_name=n.split('.')[0][:30], index=False)
            st.download_button("Descargar Base de Datos .XLSX", output_x.getvalue(), f"Reporte_Meru_{sel_month}.xlsx")
    else:
        st.warning("Debe cargar archivos para habilitar la exportación.")

st.markdown("<div style='text-align:center; padding:30px; opacity:0.4; font-size:0.7rem;'>MERU NETWORKS SECURITY SYSTEM © 2026 | TODOS LOS DERECHOS RESERVADOS</div>", unsafe_allow_html=True)
