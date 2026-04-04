import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os
import io

# Librerías para exportación (Debes instalarlas: pip install python-docx xlsxwriter)
from docx import Document
from docx.shared import Inches

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru Networks | Enterprise Hub", page_icon="📡", layout="wide")

# --- ESTILOS CORPORATIVOS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafd; color: #1a202c; font-family: 'Inter', sans-serif; }
    .metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center; }
    .m-value { color: #0366d6; font-size: 1.8rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO Y REGISTRO ---
if 'data_registry' not in st.session_state:
    st.session_state.data_registry = pd.DataFrame(columns=['Fecha_Import', 'Archivo', 'Tipo', 'Registros'])
if 'ticket_db' not in st.session_state:
    st.session_state.ticket_db = []

# --- FUNCIONES DE LIMPIEZA Y PROCESAMIENTO ---
def process_csv(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip = 0
    for i, line in enumerate(content):
        if any(k in line for k in ["Date", "Time", "Octets", "Eb/No", "ZONA", "NOMBRE ISP"]):
            skip = i
            break
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip)
    df.columns = [str(c).strip().replace('"', '') for c in df.columns]
    # Intentar normalizar columna de fecha para análisis cronológico
    for col in df.columns:
        if 'Date' in col or 'FECHA' in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# --- MÓDULO DE EXPORTACIÓN ---
def export_to_word(df_list, titles):
    doc = Document()
    doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    doc.add_paragraph(f"Fecha de generación: {datetime.now().strftime('%d-%m-%Y')}")
    
    for df, title in zip(df_list, titles):
        doc.add_heading(title, level=1)
        # Crear tabla
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- HEADER ---
c1, c2 = st.columns([1, 2])
with c1:
    if os.path.exists("image_4eb8c8.png"): st.image("image_4eb8c8.png", width=250)
    else: st.title("MERU NETWORKS")
with c2:
    st.markdown("<div style='text-align:right;'><h3>NOC COMMAND CENTER</h3><p>Registro y Gestión de Datos Críticos</p></div>", unsafe_allow_html=True)

# --- SIDEBAR: IMPORTACIÓN Y FILTROS ---
with st.sidebar:
    st.header("📥 DATA INGESTION")
    uploaded_files = st.file_uploader("Subir modelos (CSV/Excel)", accept_multiple_files=True)
    
    if uploaded_files:
        for f in uploaded_files:
            if f.name not in st.session_state.data_registry['Archivo'].values:
                df_tmp = process_csv(f)
                new_entry = {
                    'Fecha_Import': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Archivo': f.name,
                    'Tipo': 'Señal/Tráfico' if 'Eb/No' in "".join(df_tmp.columns) else 'Gestión/Fallas',
                    'Registros': len(df_tmp)
                }
                st.session_state.data_registry = pd.concat([st.session_state.data_registry, pd.DataFrame([new_entry])], ignore_index=True)

    st.markdown("---")
    st.header("📅 FILTROS CRONOLÓGICOS")
    selected_month = st.selectbox("Mes de Análisis", ["Marzo 2026", "Abril 2026"])
    specific_date = st.date_input("Fecha específica", datetime(2026, 3, 1))

# --- TABS PRINCIPALES ---
t_reg, t_analisis, t_export = st.tabs(["📋 REGISTRO DE DATA", "📈 ANÁLISIS CRONOLÓGICO", "📥 MÓDULO EXPORTAR"])

# TAB 1: REGISTRO DE DATA IMPORTADA
with t_reg:
    st.subheader("Historial de Importaciones")
    st.dataframe(st.session_state.data_registry, use_container_width=True)
    st.info("Este registro permite auditar qué archivos han sido procesados en el sistema.")

# TAB 2: ANÁLISIS POR MES Y FECHA
with t_analisis:
    st.subheader(f"Análisis Detallado: {selected_month}")
    if uploaded_files:
        for f in uploaded_files:
            df = process_csv(f)
            # Filtrado por fecha si existe la columna
            date_col = next((c for c in df.columns if 'Date' in c or 'FECHA' in c), None)
            if date_col:
                df_filtered = df[df[date_col].dt.date == specific_date]
                if not df_filtered.empty:
                    st.write(f"Datos para el {specific_date} en {f.name}")
                    st.dataframe(df_filtered.head())
                else:
                    st.caption(f"Sin registros específicos para {specific_date} en {f.name}")
    else:
        st.warning("Cargue datos para activar el análisis temporal.")

# TAB 3: MÓDULO DE EXPORTACIÓN (WORD / EXCEL)
with t_export:
    st.subheader("Generación de Informes Oficiales")
    st.write("Exporte los datos procesados manteniendo la estructura de los modelos originales.")
    
    if uploaded_files:
        col_ex1, col_ex2 = st.columns(2)
        
        # Preparar datos para exportar
        export_list = []
        names_list = []
        for f in uploaded_files:
            export_list.append(process_csv(f))
            names_list.append(f.name)

        with col_ex1:
            st.markdown("### 📄 Formato Word")
            word_data = export_to_word(export_list, names_list)
            st.download_button(
                label="Descargar Informe .DOCX",
                data=word_data,
                file_name=f"Informe_Meru_{selected_month.replace(' ','_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        with col_ex2:
            st.markdown("### Excel Corporativo")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for df, name in zip(export_list, names_list):
                    # Acortar nombre de pestaña para Excel
                    df.to_excel(writer, sheet_name=name[:30], index=False)
            
            st.download_button(
                label="Descargar Reporte .XLSX",
                data=output.getvalue(),
                file_name=f"Data_Meru_{selected_month.replace(' ','_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Debe haber datos cargados para habilitar la exportación.")

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.3; font-size:0.8rem;'>MERU NETWORKS ENTERPRISE SOLUTION © 2026</p>", unsafe_allow_html=True)
