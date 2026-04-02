import streamlit as st
import pandas as pd
import io
import time
import requests
from docx import Document
from docx.shared import Pt
import openpyxl

# --- Configuración ---
st.set_page_config(page_title="Meru NOC - Reporte Mensual", layout="wide")

# --- Constantes de IA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # Gestionado internamente
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_analysis(context_text):
    """Analiza los datos de los CSV para generar el resumen ejecutivo del informe."""
    prompt = f"""
    Eres un analista de operaciones de red (NOC) para Meru-Networks. 
    Analiza los siguientes datos de tráfico, fallas y reclamos del mes de marzo 2026:
    {context_text}
    
    Proporciona un 'Resumen Ejecutivo' de 3 párrafos resaltando:
    1. Disponibilidad general y eventos climáticos/astronómicos.
    2. Resumen de tráfico (nodos más activos).
    3. Eficiencia en la resolución de fallas y reclamos.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Error al generar análisis automático. Por favor, revise los datos manualmente."
    return "Análisis no disponible."

# --- Procesamiento de Archivos ---
def process_uploaded_files(files):
    data_frames = {}
    for file in files:
        name = file.name.lower()
        # Identificar archivos por palabras clave en el nombre
        if "data usage" in name:
            data_frames['uso'] = pd.read_csv(file, skiprows=3)
        elif "statistics (43)" in name:
            data_frames['octetos'] = pd.read_csv(file)
        elif "statistics (42)" in name:
            data_frames['ebno'] = pd.read_csv(file)
        elif "isp" in name:
            data_frames['fallas_isp'] = pd.read_csv(file, skiprows=3)
        elif "reclamos" in name:
            data_frames['reclamos'] = pd.read_csv(file, skiprows=3)
        elif "internas" in name:
            data_frames['fallas_internas'] = pd.read_csv(file, skiprows=3)
    return data_frames

# --- Generación de Documentos ---
def create_excel_report(df_isp, df_reclamos, df_internas):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if df_isp is not None: df_isp.to_excel(writer, sheet_name='REPORTE ISP', index=False)
        if df_reclamos is not None: df_reclamos.to_excel(writer, sheet_name='REPORTE RECLAMOS', index=False)
        if df_internas is not None: df_internas.to_excel(writer, sheet_name='FALLAS INTERNAS', index=False)
    return output.getvalue()

def create_word_report(summary, tables_dict):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    doc.add_paragraph("Periodo: Marzo 2026")
    
    doc.add_heading('1. RESUMEN EJECUTIVO (Analizado por IA)', level=1)
    doc.add_paragraph(summary)

    sections = {
        'fallas_isp': '2. REPORTE DE FALLAS PROVEEDORES (ISP)',
        'reclamos': '3. REPORTE DE ATENCIÓN DE RECLAMOS',
        'fallas_internas': '4. REPORTE DE FALLAS INTERNAS'
    }

    for key, title in sections.items():
        if key in tables_dict and tables_dict[key] is not None:
            doc.add_heading(title, level=1)
            df = tables_dict[key].dropna(how='all').head(15) # Limitar para el doc
            table = doc.add_table(rows=1, cols=len(df.columns))
            table.style = 'Table Grid'
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)
            for _, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, val in enumerate(row):
                    row_cells[i].text = str(val)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- UI Principal ---
st.title("📡 Gestor de Informes Mensuales NOC")
st.markdown("### Importación de Datos CSV para Análisis de Marzo 2026")

with st.sidebar:
    st.header("Configuración")
    uploaded_files = st.file_uploader("Cargar archivos CSV (Uso, EbNo, ISP, Reclamos, Internas)", accept_multiple_files=True)
    st.info("Sube los archivos CSV exportados para que la IA los analice.")

if uploaded_files:
    dfs = process_uploaded_files(uploaded_files)
    
    tab1, tab2, tab3 = st.tabs(["📊 Vista de Datos", "🤖 Análisis IA", "📥 Exportar"])

    with tab1:
        col1, col2 = st.columns(2)
        if 'fallas_isp' in dfs:
            with col1: 
                st.subheader("Fallas ISP")
                st.dataframe(dfs['fallas_isp'].head(5))
        if 'reclamos' in dfs:
            with col2:
                st.subheader("Reclamos Abonados")
                st.dataframe(dfs['reclamos'].head(5))
        
        if 'uso' in dfs:
            st.subheader("Tráfico (Data Usage)")
            st.line_chart(dfs['uso'].set_index('Date').iloc[:, :5]) # Primeras 5 columnas para visualización

    with tab2:
        st.subheader("Análisis Estratégico de la IA")
        if st.button("Ejecutar Análisis de Marzo 2026"):
            # Crear contexto limitado para la IA
            context = ""
            if 'fallas_isp' in dfs: context += f"Fallas ISP: {dfs['fallas_isp'].shape[0]} registros. "
            if 'uso' in dfs: context += f"Tráfico Promedio: {dfs['uso'].mean().mean():.2f} MB. "
            
            with st.spinner("Gemini analizando patrones de red..."):
                analysis_result = call_gemini_analysis(context)
                st.session_state['ia_report'] = analysis_result
                st.write(analysis_result)
        elif 'ia_report' in st.session_state:
            st.write(st.session_state['ia_report'])

    with tab3:
        st.subheader("Generación de Entregables Mensuales")
        if 'ia_report' in st.session_state:
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("📄 **Informe Word**")
                word_data = create_word_report(st.session_state['ia_report'], dfs)
                st.download_button(
                    "Descargar Informe Word (.docx)", 
                    word_data, 
                    "Informe_Gestion_NOC_Marzo_2026.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            with col_b:
                st.write("Excel **Consolidado de Tablas**")
                excel_data = create_excel_report(
                    dfs.get('fallas_isp'), 
                    dfs.get('reclamos'), 
                    dfs.get('fallas_internas')
                )
                st.download_button(
                    "Descargar Excel de Gestión (.xlsx)", 
                    excel_data, 
                    "Tablas_Gestion_NOC_Marzo_2026.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("Debes ejecutar el Análisis IA primero para generar los reportes.")

else:
    st.warning("Esperando carga de archivos CSV para iniciar el proceso...")
