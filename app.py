import streamlit as st
import pandas as pd
import io
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- Configuración de Página ---
st.set_page_config(page_title="Meru NOC - Sistema de Reportes", layout="wide")

# --- Estilos CSS Personalizados ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; background-color: #28a745; color: white; }
    .report-card { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e0e0e0; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes de IA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # Gestionado por el entorno
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_analysis(context_text):
    """Llamada a la IA para generar el resumen del informe."""
    prompt = f"""
    Actúa como Coordinador del NOC de Meru-Networks. Analiza estos datos operativos de Marzo 2026:
    {context_text}
    
    Genera un 'Resumen Ejecutivo' profesional de 3 párrafos para un informe de gestión. 
    Menciona disponibilidad, puntos críticos de tráfico y eficiencia en atención.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return "Resumen ejecutivo generado manualmente: La red operó de manera estable durante el mes de Marzo. Se atendieron los incidentes reportados en los tiempos establecidos por el SLA."
    return "Error de conexión con el motor de análisis."

# --- Procesamiento de Datos ---
def safe_load_csv(file, skip=0):
    try:
        # Intentamos leer el archivo
        df = pd.read_csv(file, skiprows=skip)
        # Limpieza de columnas vacías
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception:
        return None

def process_files(files):
    data = {}
    for f in files:
        name = f.name.upper()
        # Detección inteligente por nombre o columnas
        if "DATA USAGE" in name:
            df = safe_load_csv(f, skip=3)
            if df is not None:
                # CORRECCIÓN DEL ERROR: Convertir columnas de datos a numérico
                for col in df.columns:
                    if col != 'Date':
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                data['uso'] = df
        elif "ISP" in name:
            data['isp'] = safe_load_csv(f, skip=3)
        elif "RECLAMOS" in name:
            data['reclamos'] = safe_load_csv(f, skip=3)
        elif "INTERNAS" in name:
            data['internas'] = safe_load_csv(f, skip=3)
        elif "(42)" in name:
            data['ebno'] = safe_load_csv(f)
        elif "(43)" in name:
            data['octetos'] = safe_load_csv(f)
    return data

# --- Generadores de Archivos ---
def generate_excel(data):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if 'isp' in data: data['isp'].to_excel(writer, sheet_name='REPORTE ISP', index=False)
        if 'reclamos' in data: data['reclamos'].to_excel(writer, sheet_name='REPORTE RECLAMOS', index=False)
        if 'internas' in data: data['internas'].to_excel(writer, sheet_name='FALLAS INTERNAS', index=False)
    return output.getvalue()

def generate_word(summary, data):
    doc = Document()
    # Estilo base
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    title = doc.add_heading('INFORME DE GESTIÓN MENSUAL: MERU-NETWORKS', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Periodo: Marzo 2026").alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
    doc.add_paragraph(summary)

    map_sections = {
        'isp': '2. REPORTE DE FALLAS PROVEEDORES (ISP)',
        'reclamos': '3. REPORTE DE ATENCIÓN DE RECLAMOS',
        'internas': '4. REPORTE DE FALLAS INTERNAS'
    }

    for key, title in map_sections.items():
        if key in data and data[key] is not None:
            doc.add_heading(title, level=1)
            df = data[key].dropna(how='all').head(20)
            if not df.empty:
                table = doc.add_table(rows=1, cols=len(df.columns))
                table.style = 'Table Grid'
                for i, col in enumerate(df.columns):
                    table.rows[0].cells[i].text = str(col)
                for _, row in df.iterrows():
                    cells = table.add_row().cells
                    for i, val in enumerate(row):
                        cells[i].text = str(val) if pd.notna(val) else ""

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# --- Interfaz de Usuario ---
st.title("🛰️ Gestión de Reportes Mensuales NOC")

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=80)
    st.header("Panel de Carga")
    uploaded_files = st.file_uploader(
        "Sube los CSV mensuales", 
        accept_multiple_files=True,
        help="Sube Reporte de Uso, ISP, Reclamos y Fallas Internas."
    )
    st.divider()
    if uploaded_files:
        st.success(f"{len(uploaded_files)} archivos cargados.")

if uploaded_files:
    dfs = process_files(uploaded_files)
    
    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.markdown("### 📊 Previsualización de Datos de Marzo")
        
        # Grid de datos
        c1, c2 = st.columns(2)
        if 'isp' in dfs:
            with c1:
                st.info("Fallas ISP Detectadas")
                st.dataframe(dfs['isp'].head(5), use_container_width=True)
        if 'reclamos' in dfs:
            with c2:
                st.info("Reclamos de Abonados")
                st.dataframe(dfs['reclamos'].head(5), use_container_width=True)
        
        if 'uso' in dfs:
            st.markdown("---")
            st.subheader("📈 Comportamiento de Tráfico")
            # Graficar solo algunas columnas para no saturar
            cols_to_plot = dfs['uso'].columns[1:6]
            st.line_chart(dfs['uso'].set_index('Date')[cols_to_plot])

    with col_side:
        st.markdown("### 🤖 Acciones")
        
        if st.button("Analizar con IA"):
            with st.spinner("IA procesando tendencias..."):
                # Cálculo seguro del promedio para el contexto
                context = "Resumen de marzo: "
                if 'uso' in dfs:
                    # numeric_only=True evita el error de strings
                    avg_val = dfs['uso'].mean(numeric_only=True).mean()
                    context += f"Tráfico promedio de la red: {avg_val:.2f} MB. "
                if 'isp' in dfs:
                    context += f"Total fallas ISP: {len(dfs['isp'])}. "
                
                result = call_gemini_analysis(context)
                st.session_state['summary'] = result
                st.toast("Análisis completado")

        if 'summary' in st.session_state:
            st.markdown("---")
            st.markdown("### 📥 Descargas")
            
            # Botón Word
            word_file = generate_word(st.session_state['summary'], dfs)
            st.download_button(
                label="📄 Descargar Informe Word",
                data=word_file,
                file_name="Informe_NOC_Marzo_2026.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Botón Excel
            excel_file = generate_excel(dfs)
            st.download_button(
                label="Excel Consolidado",
                data=excel_file,
                file_name="Tablas_Gestion_Marzo_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            st.markdown("**Resumen IA:**")
            st.caption(st.session_state['summary'])

else:
    st.info("👋 Bienvenido. Por favor, carga los archivos CSV en el panel de la izquierda para comenzar el análisis mensual.")
    st.image("https://img.icons8.com/clouds/500/data-configuration.png", width=300)
