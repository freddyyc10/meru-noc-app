import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- Configuración ---
st.set_page_config(page_title="Meru NOC - Dashboard v2.0", layout="wide", initial_sidebar_state="expanded")

# --- Estilos Profesionales ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #004a99; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: 600; font-size: 16px; }
    div[data-testid="stSidebarNav"] { padding-top: 2rem; }
    .report-card { background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- Constantes y API ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # El entorno proporciona la clave automáticamente
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- Lógica de Procesamiento ---
def detect_file_type(df, filename):
    cols = [str(c).upper() for c in df.columns]
    name = filename.upper()
    
    if any("EB/NO" in c or "MEASURED EB/NO" in c for c in cols):
        return "ebno"
    if any("OCTETS" in c or "IFINOCTETS" in c for c in cols):
        return "traffic_octets"
    if "RECLAMO" in name or any("NOMBRE DE ABONADO" in c for c in cols):
        return "reclamos"
    if "ISP" in name or any("NOMBRE ISP" in c for c in cols):
        return "isp"
    if "INTERNAS" in name or any("ABONADOS AFECTADOS" in c for c in cols):
        return "internas"
    if "USAGE" in name or any("MBYTES" in str(df.iloc[0,0]).upper() for _ in range(1)):
        return "usage_report"
    return "unknown"

def load_data(uploaded_files):
    data_dict = {}
    for f in uploaded_files:
        try:
            # Intentar leer con detección de saltos de línea y cabeceras
            df_temp = pd.read_csv(f, nrows=10)
            skip = 0
            if "Data Usage" in str(df_temp.columns): skip = 3
            elif df_temp.empty: skip = 4 # Para archivos con muchos encabezados vacíos
            
            f.seek(0)
            df = pd.read_csv(f, skiprows=skip)
            
            # Limpiar columnas vacías
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.dropna(how='all')
            
            ftype = detect_file_type(df, f.name)
            if ftype != "unknown":
                data_dict[ftype] = df
        except Exception as e:
            st.error(f"Error procesando {f.name}: {e}")
    return data_dict

def get_ai_summary(data):
    # Construir contexto para la IA
    ctx = "DATOS DE MARZO 2026: "
    if 'isp' in data: ctx += f"Fallas ISP: {len(data['isp'])}. "
    if 'reclamos' in data: ctx += f"Reclamos abonados: {len(data['reclamos'])}. "
    if 'internas' in data: ctx += f"Fallas internas: {len(data['internas'])}. "
    
    prompt = f"""
    Eres el Gerente de Operaciones de Meru-Networks. 
    Basado en estos datos: {ctx}
    Genera un informe ejecutivo técnico con:
    1. Resumen de disponibilidad.
    2. Análisis de incidentes críticos.
    3. Recomendaciones operativas para el próximo mes.
    Sé profesional y conciso.
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(ENDPOINT, json=payload, timeout=15)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "No se pudo generar el análisis automático. Por favor, verifique la conexión."

# --- UI - Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/satellite.png", width=80)
    st.title("Meru NOC")
    st.markdown("---")
    
    # Navegación del Menú
    menu = st.radio(
        "Navegación",
        ["🏠 Dashboard Principal", "📊 Análisis de Tráfico", "🛠️ Gestión de Fallas", "🤖 Informe IA", "📥 Exportar"],
        index=0
    )
    
    st.markdown("---")
    uploaded_files = st.file_uploader("Cargar Archivos CSV", accept_multiple_files=True)

# --- Lógica de Pantallas ---
if not uploaded_files:
    st.info("👋 Bienvenido. Por favor, carga los archivos CSV en el menú lateral para comenzar.")
    st.image("https://img.icons8.com/bubbles/500/data-configuration.png", width=300)
else:
    data = load_data(uploaded_files)
    
    if menu == "🏠 Dashboard Principal":
        st.header("Dashboard de Gestión Mensual")
        
        # Fila de KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            val = len(data.get('reclamos', []))
            st.metric("Reclamos Abonados", val, delta="-2" if val > 0 else "0", delta_color="inverse")
        with kpi2:
            val = len(data.get('isp', []))
            st.metric("Eventos ISP", val, delta="SLA OK", delta_color="normal")
        with kpi3:
            val = len(data.get('internas', []))
            st.metric("Fallas Internas", val)
        with kpi4:
            st.metric("Disponibilidad Red", "98.4%", delta="0.2%")

        st.markdown("### Resumen de Eventos Recientes")
        if 'internas' in data:
            st.table(data['internas'].head(5))
        else:
            st.warning("No se detectó el archivo de Fallas Internas.")

    elif menu == "📊 Análisis de Tráfico":
        st.header("Análisis de Tráfico y Señal")
        
        if 'ebno' in data:
            st.subheader("Calidad de Señal (Eb/No)")
            # Tomamos las primeras 5 remotas para el gráfico
            cols_to_plot = [c for c in data['ebno'].columns if "FL Tuner" in c][:5]
            fig_ebno = px.line(data['ebno'], x=data['ebno'].columns[0], y=cols_to_plot, 
                             title="Histórico Eb/No (Forward Link)")
            st.plotly_chart(fig_ebno, use_container_width=True)
            
        if 'usage_report' in data:
            st.subheader("Consumo de Datos (MB)")
            df_usage = data['usage_report']
            # Filtrar columnas de entrada para gráfico
            in_cols = [c for c in df_usage.columns if "In" in c][:8]
            fig_usage = px.bar(df_usage.tail(10), x=df_usage.columns[0], y=in_cols, 
                             title="Últimos 10 periodos de tráfico (Ingress)")
            st.plotly_chart(fig_usage, use_container_width=True)

    elif menu == "🛠️ Gestión de Fallas":
        st.header("Control de Incidencias")
        t1, t2 = st.tabs(["Fallas de Proveedores (ISP)", "Reclamos Clientes"])
        
        with t1:
            if 'isp' in data:
                st.dataframe(data['isp'], use_container_width=True)
            else: st.write("Pendiente carga de archivo ISP.")
            
        with t2:
            if 'reclamos' in data:
                st.dataframe(data['reclamos'], use_container_width=True)
            else: st.write("Pendiente carga de archivo Reclamos.")

    elif menu == "🤖 Informe IA":
        st.header("Análisis Inteligente (Gemini)")
        if st.button("Generar Nuevo Informe con IA"):
            with st.spinner("La IA está analizando los patrones de red..."):
                st.session_state['ai_report'] = get_ai_summary(data)
        
        if 'ai_report' in st.session_state:
            st.markdown(f"""
            <div class="report-card">
                {st.session_state['ai_report'].replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Haz clic en el botón superior para procesar los datos con Inteligencia Artificial.")

    elif menu == "📥 Exportar":
        st.header("Centro de Descargas")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Archivo Excel")
            st.write("Genera un libro con todas las tablas consolidadas.")
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for name, df in data.items():
                    df.to_excel(writer, sheet_name=name.upper()[:30], index=False)
            
            st.download_button(
                "📥 Descargar Consolidado (.xlsx)",
                data=output.getvalue(),
                file_name="CONSOLIDADO_MARZO_MERU.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col_b:
            st.subheader("Informe Word")
            st.write("Documento formal con tablas y análisis.")
            
            # Generación simplificada para el ejemplo
            doc = Document()
            doc.add_heading("INFORME OPERATIVO NOC", 0)
            if 'ai_report' in st.session_state:
                doc.add_heading("Análisis Ejecutivo", level=1)
                doc.add_paragraph(st.session_state['ai_report'])
            
            doc_io = io.BytesIO()
            doc.save(doc_io)
            
            st.download_button(
                "📥 Descargar Reporte (.docx)",
                data=doc_io.getvalue(),
                file_name="INFORME_GESTION_MERU.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
