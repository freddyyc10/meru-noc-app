import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
import os

# Librerías necesarias: pip install python-docx xlsxwriter
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru Networks | Intelligence Hub", page_icon="📡", layout="wide")

# --- FUNCIONES DE PROCESAMIENTO ---
def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if any(key in line for key in ["Date", "Time", "Octets", "Eb/No", "FECHA", "ZONA", "NOMBRE ISP"]):
            skip_rows = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip_rows)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- MOTOR DE EXPORTACIÓN ESTRUCTURADO (WORD) ---
def export_structured_docx(processed_data, month_text):
    doc = Document()
    
    # Estilo de Título Principal
    title = doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f"Periodo: {month_text}")
    doc.add_paragraph("Departamento: Operaciones de Red (NOC) / Soporte Técnico")

    # 1. Resumen Ejecutivo
    doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
    doc.add_paragraph("Durante el periodo reportado, la red operó bajo parámetros nominales. (Completar con análisis de IA o manual).")

    # Mapeo de secciones según los archivos cargados
    sections = {
        "FALLAS INTERNAS": "2. REPORTE DE FALLAS INTERNAS (GESTIÓN PROPIA)",
        "ISP": "3. REPORTE DE FALLAS DE PROVEEDORES (ISP)",
        "RECLAMOS": "4. ATENCIÓN DE RECLAMOS DEL ABONADO"
    }

    for name, df in processed_data.items():
        title_text = "REPORTE DETALLADO"
        for key, val in sections.items():
            if key in name.upper():
                title_text = val
        
        doc.add_heading(title_text, level=1)
        
        # Crear tabla con la estructura del modelo
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        for i, col_name in enumerate(df.columns):
            hdr_cells[i].text = col_name
            
        # Añadir filas (limitado a las primeras 50 para el informe escrito)
        for _, row in df.head(50).iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
        
        doc.add_paragraph("\n")

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- UI PRINCIPAL ---
c1, c2 = st.columns([1, 2])
with c1:
    if os.path.exists("image_4eb8c8.png"): st.image("image_4eb8c8.png", width=250)
    else: st.title("MERU NETWORKS")
with c2:
    st.markdown("<div style='text-align:right; padding-top:10px;'><h3>NOC OPERATIONAL HUB v9.0</h3></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("📥 CARGA DE MODELOS")
    files = st.file_uploader("Subir CSV de Fallas, ISP o Reclamos", accept_multiple_files=True)
    st.markdown("---")
    sel_month = st.selectbox("Preparando documentos para:", ["Marzo 2026", "Abril 2026", "Mayo 2026"])

# --- PESTAÑAS ---
tab_dash, tab_tickets, tab_export = st.tabs(["📊 DASHBOARD ANALÍTICO", "🎫 GESTIÓN DE TICKETS", "📥 EXPORTACIÓN DE INFORMES"])

processed_data = {}
if files:
    for f in files:
        processed_data[f.name] = get_clean_df(f)

with tab_dash:
    if files:
        for name, df in processed_data.items():
            with st.expander(f"Vista previa: {name}"):
                st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("Cargue los archivos de gestión en la barra lateral.")

with tab_tickets:
    st.subheader("Registro de Incidentes en Sesión")
    if files:
        st.write("Archivos vinculados al reporte mensual:")
        for f in files:
            st.caption(f"✅ {f.name}")

with tab_export:
    st.subheader("Centro de Generación de Documentos")
    st.write(f"Estructura basada en los modelos oficiales de **Meru Networks**.")
    
    if processed_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Informe Word")
            st.write("Genera el .docx con encabezados, tablas de fallas y reclamos formateadas.")
            docx_bytes = export_structured_docx(processed_data, sel_month)
            st.download_button(
                label="Generar Informe Word (.docx)",
                data=docx_bytes,
                file_name=f"Informe_Gestion_Meru_{sel_month.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        with col2:
            st.markdown("#### 📊 Base de Datos Excel")
            st.write("Exporta todas las tablas a un libro Excel con pestañas independientes.")
            output_xlsx = io.BytesIO()
            with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
                for name, df in processed_data.items():
                    # Limpiar nombre de la pestaña (máx 31 caracteres)
                    sheet_name = name.split('.')[0][:30]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.download_button(
                label="Generar Base de Datos Excel (.xlsx)",
                data=output_xlsx.getvalue(),
                file_name=f"Reporte_Consolidado_Meru_{sel_month.replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No hay datos cargados para exportar. Por favor, suba los archivos de gestión.")

st.markdown("<p style='text-align:center; opacity:0.2; margin-top:50px;'>MERU NETWORKS SECURITY SYSTEM © 2026</p>", unsafe_allow_html=True)
