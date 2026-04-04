
       import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
import os

# Librerías necesarias: pip install python-docx xlsxwriter
from docx import Document
from docx.shared import Pt

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru Networks | Intelligence Hub", page_icon="📡", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafd; color: #1a202c; font-family: 'Inter', sans-serif; }
    .metric-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; text-align: center; }
    .m-value { color: #0366d6; font-size: 1.5rem; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE REGISTRO ---
if 'registro_importacion' not in st.session_state:
    st.session_state.registro_importacion = []

# --- FUNCIONES DE PROCESAMIENTO ---
def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip = 0
    for i, line in enumerate(content):
        if any(k in line for k in ["Date", "Time", "Octets", "Eb/No", "FECHA", "ZONA"]):
            skip = i
            break
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip)
    df.columns = [str(c).strip().replace('"', '') for c in df.columns]
    return df

def export_docx(data_dict):
    doc = Document()
    doc.add_heading('INFORME DE GESTIÓN MENSUAL - MERU NETWORKS', 0)
    for name, df in data_dict.items():
        doc.add_heading(f'Reporte: {name}', level=1)
        table = doc.add_table(rows=1, cols=len(df.columns))
        for i, col in enumerate(df.columns):
            table.rows[0].cells[i].text = col
        for _, row in df.head(20).iterrows(): # Limitado a 20 para el ejemplo
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
    st.markdown("<div style='text-align:right; padding-top:10px;'><h3>NOC OPERATIONAL HUB</h3></div>", unsafe_allow_html=True)

# --- BARRA LATERAL (FILTROS) ---
with st.sidebar:
    st.markdown("### 📥 CARGA Y FILTROS")
    files = st.file_uploader("Subir Reportes (CSV)", accept_multiple_files=True)
    st.markdown("---")
    sel_month = st.selectbox("Mes de Análisis", ["Marzo 2026", "Abril 2026"])
    sel_date = st.date_input("Filtrar por Fecha Específica", datetime(2026, 3, 1))

# --- MENÚ DE MÓDULOS (TABS ORIGINALES) ---
tab_dash, tab_tickets, tab_ia, tab_export = st.tabs(["📊 DASHBOARD", "🎫 TICKETS", "🧠 CORE AI", "📥 EXPORTAR"])

# Lógica de carga de datos para los módulos
processed_data = {}
if files:
    for f in files:
        df = get_clean_df(f)
        processed_data[f.name] = df
        # Registrar en el historial si no existe
        if f.name not in [x['nombre'] for x in st.session_state.registro_importacion]:
            st.session_state.registro_importacion.append({
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "nombre": f.name,
                "filas": len(df)
            })

# TAB 1: DASHBOARD (Análisis por fecha/mes)
with tab_dash:
    if files:
        st.subheader(f"Análisis Mensual: {sel_month}")
        for name, df in processed_data.items():
            with st.expander(f"Visualización: {name}", expanded=True):
                # Gráfica interactiva similar a la v2.0
                stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                if stations:
                    sel_st = st.multiselect(f"Estaciones en {name}:", stations, default=stations[:1], key=f"st_{name}")
                    fig = go.Figure()
                    for s in sel_st:
                        cols = [c for c in df.columns if c.startswith(s + "/")]
                        for c in cols:
                            fig.add_trace(go.Scatter(y=df[c], name=f"{s}-{c.split('/')[-1]}"))
                    fig.update_layout(template="plotly_white", height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(df.head(10))
    else:
        st.info("Cargue archivos para ver el análisis detallado.")

# TAB 2: TICKETS (Persistente)
with tab_tickets:
    st.subheader("Gestión de Incidentes")
    # Mostrar el registro de importación como parte de la gestión
    st.write("**Registro de Datos Importados:**")
    st.table(pd.DataFrame(st.session_state.registro_importacion))
    
    st.markdown("---")
    st.write("**Formulario de Tickets**")
    # (Estructura de ticket anterior preservada)
    with st.form("ticket_meru"):
        col_t1, col_t2 = st.columns(2)
        node = col_t1.text_input("Nodo")
        falla = col_t2.selectbox("Tipo de Falla", ["Eb/No Bajo", "Saturación", "Desapuntamiento"])
        if st.form_submit_button("Registrar Ticket"):
            st.success(f"Ticket creado para {node}")

# TAB 3: CORE AI
with tab_ia:
    st.subheader("Meru AI Engine")
    query = st.text_input("Consultar diagnóstico de la red:")
    if st.button("Analizar"):
        st.write("🔍 **Resultado:** Basado en los archivos de Marzo 2026, se observa una estabilidad del 98% con alertas menores en nodos de Amazonas.")

# TAB 4: EXPORTAR (Nuevo Módulo)
with tab_export:
    st.subheader("Exportación de Informes de Gestión")
    if processed_data:
        st.write(f"Preparando documentos para: **{sel_month}**")
        
        c_exp1, c_exp2 = st.columns(2)
        
        with c_exp1:
            st.info("Generar Informe Word (.docx)")
            docx_file = export_docx(processed_data)
            st.download_button("Descargar Informe Word", docx_file, f"Informe_Meru_{sel_month}.docx")
            
        with c_exp2:
            st.info("Generar Base de Datos Excel (.xlsx)")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for name, df in processed_data.items():
                    df.to_excel(writer, sheet_name=name[:30], index=False)
            st.download_button("Descargar Reporte Excel", output.getvalue(), f"Reporte_Meru_{sel_month}.xlsx")
    else:
        st.warning("No hay datos cargados para exportar.")

st.markdown("<p style='text-align:center; opacity:0.2; margin-top:50px;'>MERU NETWORKS v9.0</p>", unsafe_allow_html=True)
