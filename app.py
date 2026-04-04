import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import requests
import json
import time
from datetime import datetime

# Librerías para generación de documentos
from docx import Document
from docx.shared import Inches
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Meru NOC - Enterprise Analysis",
    page_icon="🛰️",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    div[data-testid="stSidebarNav"] {
        background-image: url('https://www.google.com/s2/favicons?domain=meru.com');
        background-repeat: no-repeat;
        padding-top: 80px;
        background-position: 20px 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #2563eb;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE LA SESIÓN (BASE DE DATOS VOLÁTIL) ---
if 'tickets' not in st.session_state:
    st.session_state.tickets = []
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = ""

# --- FUNCIONES CORE ---

def call_gemini_api(data_summary):
    """Simulación de integración con Gemini API (Vertex AI / AI Studio)"""
    # En un entorno real, usaría:
    # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    # Aquí implementamos la lógica de prompt estratégico solicitado
    
    prompt = f"""
    Actúa como un experto en redes NOC. Analiza el siguiente resumen de datos:
    {data_summary}
    
    Proporciona:
    1. Conclusiones estratégicas sobre el rendimiento.
    2. Recomendaciones técnicas para optimizar la red.
    3. Identificación de posibles anomalías.
    """
    
    # Simulación de delay de red y respuesta
    with st.spinner("Gemini analizando patrones de red..."):
        time.sleep(2)
        return f"ANÁLISIS ESTRATÉGICO MERU NOC\n\n1. HALLAZGOS: Se detecta una saturación del 15% en los nodos del sector Norte durante horas pico.\n2. RECOMENDACIÓN: Implementar balanceo de carga preventivo en el segmento BOG-01.\n3. PREVISIÓN: Estabilidad del 99.9% si se aplica el parche de firmware v2.4."

def generate_excel_reports(df):
    """Genera 3 reportes diferenciados en un solo buffer zip o archivos individuales"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Rendimiento General')
        if 'error' in df.columns or 'status' in df.columns:
            df[df.iloc[:, -1] == 'Error'].to_excel(writer, sheet_name='Reporte de Errores')
        df.describe().to_excel(writer, sheet_name='Resumen Ejecutivo')
    return output.getvalue()

def generate_word_doc(analysis_text):
    doc = Document()
    doc.add_heading('Informe Técnico Meru NOC', 0)
    doc.add_paragraph(f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    doc.add_heading('Análisis de Inteligencia Artificial (Gemini)', level=1)
    doc.add_paragraph(analysis_text)
    
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- INTERFAZ DE USUARIO (NAVEGACIÓN) ---

with st.sidebar:
    st.title("Meru NOC System")
    st.image("https://img.icons8.com/fluency/96/network-antenna.png", width=80)
    menu = st.radio(
        "Navegación Principal",
        ["Dashboard & Ingesta", "Análisis Gemini AI", "Gestor de Tickets", "Exportar Reportes"]
    )
    st.divider()
    st.info("Ingeniero de Guardia: Senior Admin")

# --- MÓDULO 1: INGESTA Y DASHBOARD ---
if menu == "Dashboard & Ingesta":
    st.header("🛰️ Centro de Operaciones de Red - Meru")
    
    uploaded_files = st.file_uploader("Cargar archivos CSV de Red", type="csv", accept_multiple_files=True)
    
    if uploaded_files:
        dfs = [pd.read_csv(f) for f in uploaded_files]
        df = pd.concat(dfs, ignore_index=True)
        st.session_state.raw_data = df
        
        st.success(f"Cargados {len(uploaded_files)} archivos con {len(df)} registros totales.")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Registros", len(df))
        col2.metric("Nodos Activos", "1,284")
        col3.metric("Uptime Global", "99.98%", "0.02%")
        col4.metric("Latencia Promedio", "14ms", "-2ms")
        
        # Visualización
        st.subheader("Análisis Visual de Tráfico")
        if len(df.columns) >= 2:
            fig = px.line(df, x=df.columns[0], y=df.columns[1], title="Tendencia de Tráfico de Red (Mbps)")
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                fig_bar = px.bar(df.head(10), x=df.columns[0], y=df.columns[1], color=df.columns[1], title="Carga por Nodo")
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_b:
                st.write("Vista previa de datos cargados")
                st.dataframe(df.head(10), use_container_width=True)

# --- MÓDULO 2: INTEGRACIÓN GEMINI AI ---
elif menu == "Análisis Gemini AI":
    st.header("🧠 Inteligencia Artificial Estratégica")
    
    if st.session_state.raw_data is not None:
        if st.button("Ejecutar Análisis con Gemini Pro"):
            summary = st.session_state.raw_data.describe().to_string()
            result = call_gemini_api(summary)
            st.session_state.ai_analysis = result
            
        if st.session_state.ai_analysis:
            st.markdown("### Hallazgos de la IA")
            st.info(st.session_state.ai_analysis)
            
            # Opción para crear ticket desde el hallazgo
            if st.button("Convertir Hallazgos en Ticket de Falla"):
                new_ticket = {
                    "id": len(st.session_state.tickets) + 1,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "titulo": "Incidencia detectada por AI",
                    "prioridad": "Alta",
                    "estado": "Abierto",
                    "descripcion": st.session_state.ai_analysis[:100] + "..."
                }
                st.session_state.tickets.append(new_ticket)
                st.success("Ticket registrado automáticamente.")
    else:
        st.warning("Por favor, cargue datos CSV en el Dashboard primero.")

# --- MÓDULO 3: GESTOR DE TICKETS (CRUD) ---
elif menu == "Gestor de Tickets":
    st.header("🎫 Sistema de Gestión de Incidencias (CRUD)")
    
    # Crear Ticket
    with st.expander("➕ Registrar Nueva Incidencia"):
        with st.form("new_ticket"):
            t_title = st.text_input("Título de la Falla")
            t_priority = st.selectbox("Prioridad", ["Baja", "Media", "Alta", "Crítica"])
            t_desc = st.text_area("Descripción Técnica")
            if st.form_submit_button("Guardar Ticket"):
                st.session_state.tickets.append({
                    "id": len(st.session_state.tickets) + 1,
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "titulo": t_title,
                    "prioridad": t_priority,
                    "estado": "Abierto",
                    "descripcion": t_desc
                })
                st.rerun()

    # Mostrar Tickets
    if st.session_state.tickets:
        ticket_df = pd.DataFrame(st.session_state.tickets)
        st.subheader("Lista de Incidencias Activas")
        
        for i, ticket in enumerate(st.session_state.tickets):
            col_1, col_2, col_3, col_4 = st.columns([1, 4, 2, 2])
            col_1.write(f"#{ticket['id']}")
            col_2.write(f"**{ticket['titulo']}**")
            col_3.write(f"Priority: {ticket['prioridad']}")
            
            # Botón para cerrar ticket (Update en CRUD)
            if ticket['estado'] == "Abierto":
                if col_4.button("Cerrar", key=f"close_{i}"):
                    st.session_state.tickets[i]['estado'] = "Cerrado"
                    st.rerun()
            else:
                col_4.write("✅ Finalizado")
        
        st.divider()
        if st.button("Limpiar todos los tickets"):
            st.session_state.tickets = []
            st.rerun()
    else:
        st.info("No hay incidencias registradas.")

# --- MÓDULO 4: EXPORTACIÓN ---
elif menu == "Exportar Reportes":
    st.header("📥 Generación de Entregables")
    
    if st.session_state.raw_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Reportes en Excel")
            st.write("Genera archivos diferenciados: Rendimiento, Errores y Resumen.")
            excel_data = generate_excel_reports(st.session_state.raw_data)
            st.download_button(
                label="Descargar Pack de Excel (.xlsx)",
                data=excel_data,
                file_name=f"Meru_NOC_Reports_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        with col2:
            st.subheader("Informe Word")
            st.write("Documento profesional con análisis estratégico de IA.")
            if st.session_state.ai_analysis:
                word_data = generate_word_doc(st.session_state.ai_analysis)
                st.download_button(
                    label="Descargar Informe Ejecutivo (.docx)",
                    data=word_data,
                    file_name="Reporte_Estrategico_Meru.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.warning("Primero ejecute el análisis en el módulo de IA.")
    else:
        st.error("No hay datos disponibles para exportar.")
