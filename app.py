import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import io
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_echarts import st_echarts
from docx import Document
from docx.shared import Inches

# --- Configuración de Entorno ---
st.set_page_config(page_title="Meru NOC & Talent System", layout="wide")

# --- Constantes de IA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = ""  # Se autogestiona en el entorno
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_ai(prompt, is_json=False):
    """Lógica de IA con reintentos y soporte para JSON estructurado"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "Eres un analista experto. Si se te pide una tabla, devuelve los datos en formato CSV o lista clara."}]}
    }
    
    if is_json:
        payload["generationConfig"] = {"responseMimeType": "application/json"}

    delays = [1, 2, 4, 8, 16]
    for delay in delays:
        try:
            response = requests.post(ENDPOINT, json=payload, timeout=45)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
            if response.status_code in [429, 500, 503]:
                time.sleep(delay)
                continue
            return None
        except Exception:
            time.sleep(delay)
    return None

# --- Funciones de Documentos (Word) ---
def generate_word_report(df_list, titles, summary):
    doc = Document()
    doc.add_heading('Informe Estratégico NOC & Talent', 0)
    
    doc.add_heading('Resumen Ejecutivo de la IA', level=1)
    doc.add_paragraph(summary)
    
    for df, title in zip(df_list, titles):
        doc.add_heading(title, level=2)
        table = doc.add_table(rows=1, cols=len(df.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = str(col)
        
        for index, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, value in enumerate(row):
                row_cells[i].text = str(value)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Datos de Simulación NOC ---
def get_noc_metrics():
    times = [f"{h}:00" for h in range(24)]
    inbound = np.random.randint(400, 900, size=24).tolist()
    outbound = np.random.randint(300, 700, size=24).tolist()
    
    tickets = pd.DataFrame({
        "ID": ["T-101", "T-102", "T-103", "T-104"],
        "Prioridad": ["Alta", "Crítica", "Media", "Baja"],
        "Asunto": ["Caída de Enlace Fibra", "Latencia en Core", "Configuración BGP", "Update Firmware"],
        "Estado": ["Abierto", "En Progreso", "Pendiente", "Cerrado"]
    })
    return times, inbound, outbound, tickets

# --- UI - Sidebar ---
st.sidebar.title("📡 Meru System")
menu = st.sidebar.radio("Navegación Principal", ["Gestión NOC", "Talento & CVs", "Generador de Informes"])

# --- Pantalla 1: Gestión NOC ---
if menu == "Gestión NOC":
    st.header("📊 Centro de Operaciones de Red")
    times, inbound, outbound, tickets_df = get_noc_metrics()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Tráfico de Red en Tiempo Real (Gbps)")
        options = {
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Inbound", "Outbound"]},
            "xAxis": {"type": "category", "data": times},
            "yAxis": {"type": "value"},
            "series": [
                {"name": "Inbound", "type": "line", "data": inbound, "smooth": True},
                {"name": "Outbound", "type": "line", "data": outbound, "smooth": True}
            ]
        }
        st_echarts(options=options, height="400px")
    
    with col2:
        st.subheader("Gestión de Tickets")
        AgGrid(tickets_df, fit_columns_on_grid_load=True, theme="streamlit")
        if st.button("Analizar carga de tickets con IA"):
            analysis = call_gemini_ai(f"Analiza estos tickets y sugiere prioridades: {tickets_df.to_string()}")
            st.info(analysis)

# --- Pantalla 2: Talento & CVs ---
elif menu == "Talento & CVs":
    st.header("📂 Análisis de Candidatos con IA")
    uploaded_files = st.file_uploader("Sube CVs o Base de Datos (CSV/PDF)", accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} archivos cargados.")
        if st.button("Procesar Archivos con IA"):
            with st.spinner("La IA está extrayendo información de los archivos..."):
                # Simulación de extracción de datos por IA para generar las 3 tablas solicitadas
                prompt_extract = "Genera 3 tablas simuladas basadas en los perfiles subidos: 1. Ranking, 2. Skills Técnicas, 3. Estado de Pipeline."
                raw_data = call_gemini_ai(prompt_extract)
                
                # Aquí crearíamos los dataframes (Simulado para demostración funcional)
                df1 = pd.DataFrame({"Candidato": ["A", "B"], "Score": [90, 85]})
                df2 = pd.DataFrame({"Skill": ["Python", "Cisco"], "Nivel": ["Senior", "Junior"]})
                df3 = pd.DataFrame({"Fase": ["Entrevista", "Filtro"], "Cantidad": [5, 12]})
                
                st.session_state['talent_tables'] = [df1, df2, df3]
                st.session_state['ia_summary'] = raw_data
                st.rerun()

    if 'talent_tables' in st.session_state:
        titles = ["Ranking de Candidatos", "Matriz de Skills", "Estado del Pipeline"]
        for i, df in enumerate(st.session_state['talent_tables']):
            st.subheader(titles[i])
            AgGrid(df, fit_columns_on_grid_load=True)

# --- Pantalla 3: Generador de Informes ---
elif menu == "Generador de Informes":
    st.header("📝 Exportar Informe Word")
    
    if 'talent_tables' in st.session_state:
        st.write("Datos listos para exportación (3 Tablas de Talento + Resumen IA).")
        
        if st.button("Generar y Descargar Reporte (.docx)"):
            doc_buffer = generate_word_report(
                st.session_state['talent_tables'], 
                ["Ranking", "Skills", "Pipeline"],
                st.session_state.get('ia_summary', "Análisis no disponible")
            )
            
            st.download_button(
                label="📥 Descargar Informe Word",
                data=doc_buffer,
                file_name="Reporte_Estrategico_Meru.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Primero debes procesar datos en la sección de 'Talento & CVs'.")

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.caption("Soporta: CSV, Word Export, ECharts & AgGrid")
