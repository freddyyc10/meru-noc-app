import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
import os

# Librerías necesarias: pip install python-docx xlsxwriter
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE PÁGINA (ESTILO ORIGINAL) ---
st.set_page_config(page_title="Meru Networks | Intelligence Hub", page_icon="📡", layout="wide")

# --- ESTILOS CORPORATIVOS CLAROS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafd; color: #1a202c; font-family: 'Inter', sans-serif; }
    .nav-header { background-color: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 1rem; margin-bottom: 2rem; }
    .metric-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; text-align: center; }
    .m-value { color: #0366d6; font-size: 2rem; font-weight: 700; }
    .ticket-entry { background-color: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #58a6ff; padding: 18px; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE LIMPIEZA ---
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

# --- MOTOR DE EXPORTACIÓN (ESTRUCTURA DE TUS MODELOS) ---
def generate_meru_docx(data_dict, month_text):
    doc = Document()
    title = doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Periodo: {month_text}\nDepartamento: Operaciones de Red (NOC)")
    
    # Secciones según tu modelo .docx
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

# --- HEADER ---
c1, c2 = st.columns([1, 2])
with c1:
    if os.path.exists("image_4eb8c8.png"): st.image("image_4eb8c8.png", width=250)
    else: st.title("MERU NETWORKS")
with c2:
    st.markdown("<div style='text-align:right;'><h3>OPERATIONS COMMAND CENTER</h3></div>", unsafe_allow_html=True)

# --- SIDEBAR ORIGINAL ---
with st.sidebar:
    st.markdown("### 📥 INGESTA DE DATOS")
    uploaded_files = st.file_uploader("Cargar reportes CSV iDirect", accept_multiple_files=True)
    st.markdown("---")
    sel_month = st.selectbox("Mes para Reporte:", ["Marzo 2026", "Abril 2026"])

# --- MENU Y MODULOS ORIGINALES ---
tab_diag, tab_incident, tab_intel, tab_export = st.tabs(["📊 DASHBOARD", "🎫 TICKETS", "🧠 CORE AI", "📥 EXPORTAR"])

processed_data = {}
if uploaded_files:
    for f in uploaded_files:
        processed_data[f.name] = get_clean_df(f)

# 1. DASHBOARD (Original)
with tab_diag:
    if uploaded_files:
        st.subheader("Análisis de Telemetría")
        for name, df in processed_data.items():
            with st.expander(f"Gráfica: {name}"):
                stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                if stations:
                    sel = st.multiselect(f"Nodos:", stations, default=stations[:1], key=name)
                    fig = go.Figure()
                    for s in sel:
                        for c in [col for col in df.columns if col.startswith(s + "/")]:
                            fig.add_trace(go.Scatter(y=df[c], name=f"{s}-{c.split('/')[-1]}"))
                    st.plotly_chart(fig, use_container_width=True)
    else: st.info("Cargue archivos en la barra lateral.")

# 2. TICKETS (Original)
with tab_incident:
    st.subheader("Gestión de Incidentes")
    with st.form("t_form"):
        node = st.text_input("Nodo")
        issue = st.selectbox("Falla", ["Eb/No", "Hardware", "Energía"])
        if st.form_submit_button("Registrar"): st.success("Ticket Registrado")

# 3. CORE AI (Original)
with tab_intel:
    st.subheader("Meru AI Core")
    st.write("Análisis predictivo de la red.")

# 4. EXPORTAR (El único modificado con tus estructuras)
with tab_export:
    st.subheader("📥 Exportación de Informes de Gestión")
    st.write(f"Preparando documentos para: **{sel_month}**")
    
    if processed_data:
        col_w, col_e = st.columns(2)
        with col_w:
            st.info("Generar Informe Word (.docx)")
            docx_data = generate_meru_docx(processed_data, sel_month)
            st.download_button("Descargar Informe Word", docx_data, f"Informe_Meru_{sel_month}.docx")
        with col_e:
            st.info("Generar Base de Datos Excel (.xlsx)")
            output_x = io.BytesIO()
            with pd.ExcelWriter(output_x, engine='xlsxwriter') as writer:
                for n, df in processed_data.items():
                    df.to_excel(writer, sheet_name=n.split('.')[0][:30], index=False)
            st.download_button("Descargar Base de Datos Excel", output_x.getvalue(), f"Reporte_Meru_{sel_month}.xlsx")
    else: st.warning("Suba los archivos para exportar.")

st.markdown("<p style='text-align:center; opacity:0.2;'>MERU NETWORKS v9.0</p>", unsafe_allow_html=True)
