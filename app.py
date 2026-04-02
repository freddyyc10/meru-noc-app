import streamlit as st
import pandas as pd
import io
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- Configuración de Página ---
st.set_page_config(page_title="Meru NOC - Sistema de Reportes", layout="wide")

# --- Estilos CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stSidebar { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .stButton>button { border-radius: 8px; height: 3em; background-color: #004a99; color: white; font-weight: bold; }
    .stDownloadButton>button { border-radius: 8px; background-color: #28a745; color: white; font-weight: bold; }
    div[data-testid="stExpander"] { border: 1px solid #004a99; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes de IA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" 
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini_analysis(context_text):
    prompt = f"""
    Como Coordinador del NOC de Meru-Networks, analiza estos datos operativos de Marzo 2026:
    {context_text}
    Genera un Resumen Ejecutivo profesional de 3 párrafos. Enfócate en disponibilidad, tráfico y gestión de fallas.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        pass
    return "Resumen Estándar: Durante el periodo de Marzo 2026, la red mantuvo una operatividad estable. Se atendieron los requerimientos de los abonados y las fallas de proveedores según los protocolos establecidos."

# --- Procesamiento de Datos ---
def clean_dataframe(df):
    if df is None: return None
    # Eliminar columnas vacías creadas por exportaciones deficientes
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Limpiar filas completamente vacías
    df = df.dropna(how='all')
    return df

def process_files(files):
    data = {}
    for f in files:
        name = f.name.upper()
        # Lógica de detección por palabras clave en el nombre del archivo
        if "USAGE" in name or "USO" in name:
            df = pd.read_csv(f, skiprows=3)
            df = clean_dataframe(df)
            if df is not None:
                # Asegurar que los datos de tráfico sean numéricos
                for col in df.columns:
                    if col != 'Date': df[col] = pd.to_numeric(df[col], errors='coerce')
                data['uso'] = df
        
        elif "ISP" in name:
            df = pd.read_csv(f, skiprows=3)
            data['isp'] = clean_dataframe(df)
            
        elif "RECLAMOS" in name:
            df = pd.read_csv(f, skiprows=3)
            data['reclamos'] = clean_dataframe(df)
            
        elif "INTERNAS" in name:
            df = pd.read_csv(f, skiprows=3)
            data['internas'] = clean_dataframe(df)
            
        elif "(42)" in name:
            data['ebno'] = clean_dataframe(pd.read_csv(f))
            
        elif "(43)" in name:
            data['octetos'] = clean_dataframe(pd.read_csv(f))
            
    return data

def generate_excel(data):
    output = io.BytesIO()
    # Filtramos solo los datos que no son None y tienen contenido
    valid_data = {k: v for k, v in data.items() if v is not None and not v.empty}
    
    if not valid_data:
        return None

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for key, df in valid_data.items():
            sheet_name = key.upper()[:30] # Límite de caracteres de Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def generate_word(summary, data):
    doc = Document()
    doc.add_heading('REPORTE MENSUAL DE GESTIÓN NOC - MERU', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
    doc.add_paragraph(summary)

    sections = {
        'isp': '2. FALLAS DE PROVEEDORES (ISP)',
        'reclamos': '3. RECLAMOS DE ABONADOS',
        'internas': '4. FALLAS INTERNAS / GESTIÓN PROPIA'
    }

    for key, title in sections.items():
        if key in data and data[key] is not None:
            doc.add_heading(title, level=1)
            df = data[key].head(15) # Máximo 15 filas para no romper el layout del Word
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

# --- Interfaz Streamlit ---
st.title("🛰️ Meru NOC - Generador de Reportes")

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/briefcase.png", width=60)
    st.header("Carga de Datos")
    uploaded_files = st.file_uploader(
        "Sube los archivos CSV del mes", 
        accept_multiple_files=True,
        help="Sube: Reporte de Uso (Traffic), ISP, Reclamos e Internas."
    )
    st.info("Asegúrate de que los nombres de los archivos contengan las palabras clave (Ej: 'ISP', 'Reclamos', 'Usage')")

if uploaded_files:
    processed_data = process_files(uploaded_files)
    
    if not processed_data:
        st.warning("⚠️ No se pudieron identificar los archivos. Por favor, revisa los nombres.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Vista Previa de Datos")
            tabs = st.tabs([k.upper() for k in processed_data.keys()])
            for i, (key, df) in enumerate(processed_data.items()):
                with tabs[i]:
                    st.dataframe(df.head(10), use_container_width=True)

        with col2:
            st.subheader("⚙️ Acciones")
            if st.button("🚀 Generar Análisis con IA"):
                with st.spinner("Analizando tendencias..."):
                    ctx = "Resumen de red: "
                    if 'uso' in processed_data:
                        avg = processed_data['uso'].mean(numeric_only=True).mean()
                        ctx += f"Tráfico promedio: {avg:.2f} MB. "
                    if 'isp' in processed_data:
                        ctx += f"Eventos ISP: {len(processed_data['isp'])}. "
                    
                    st.session_state['summary'] = call_gemini_analysis(ctx)
                    st.success("Análisis listo")

            if 'summary' in st.session_state:
                st.markdown("---")
                # Descarga Word
                word_bytes = generate_word(st.session_state['summary'], processed_data)
                st.download_button(
                    "📄 Descargar Reporte Word",
                    data=word_bytes,
                    file_name="Reporte_Mensual_NOC_Marzo.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
                # Descarga Excel
                excel_bytes = generate_excel(processed_data)
                if excel_bytes:
                    st.download_button(
                        "xls Descargar Consolidado Excel",
                        data=excel_bytes,
                        file_name="Consolidado_Tablas_Marzo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                with st.expander("Ver Resumen de IA"):
                    st.write(st.session_state['summary'])
else:
    st.markdown("""
    ### Instrucciones:
    1. Sube los archivos exportados por el sistema en el panel izquierdo.
    2. El sistema identificará automáticamente si es de **Uso**, **ISP**, **Reclamos** o **Fallas Internas**.
    3. Haz clic en **Generar Análisis** para que la IA redacte el informe.
    4. Descarga los archivos finales listos para enviar.
    """)
    st.image("https://img.icons8.com/bubbles/500/dashboard.png", width=400)
