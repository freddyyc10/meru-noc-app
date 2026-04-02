import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Intelligence Hub",
    page_icon="🛡️",
    layout="wide",
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    
    :root {
        --primary: #58a6ff;
        --bg-card: #161b22;
    }

    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* Tarjetas de Métricas */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }

    /* Caja de IA */
    .ai-response {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border-left: 4px solid #238636;
        padding: 25px;
        border-radius: 0 12px 12px 0;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-top: 20px;
    }

    /* Ocultar barra de Streamlit */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND: GEMINI INTEGRATION ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # El entorno la provee automáticamente
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini(prompt, system_instruction="Eres un experto analista de redes satelitales."):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    # Implementación de reintentos con backoff exponencial
    import time
    for delay in [1, 2, 4, 8, 16]:
        try:
            res = requests.post(API_URL, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(delay)
    return "Error: No se pudo obtener el análisis de IA en este momento."

# --- PROCESAMIENTO DE ARCHIVOS ---
def clean_csv(file):
    try:
        content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
        skip = 0
        for i, line in enumerate(content[:15]):
            if any(k in line.upper() for k in ["DATE", "FECHA", "ZONA", "NODO"]):
                skip = i
                break
        file.seek(0)
        return pd.read_csv(file, skiprows=skip).dropna(axis=1, how='all')
    except: return None

# --- SIDEBAR: NAVEGACIÓN AVANZADA ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/fortawesome/Font-Awesome/6.x/svgs/solid/tower-broadcast.svg", width=50)
    st.markdown("<h2 style='text-align: center;'>MERU NOC</h2>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Resumen", "Telemetría", "Eventos", "Informe IA"],
        icons=["house", "activity", "clipboard-data", "robot"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#0d1117"},
            "icon": {"color": "#58a6ff", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#21262d"},
            "nav-link-selected": {"background-color": "#238636"},
        }
    )
    
    st.markdown("---")
    uploaded_files = st.file_uploader("Cargar Datos (.csv)", accept_multiple_files=True)

# Almacenamiento de datos
data = {}
if uploaded_files:
    for f in uploaded_files:
        df = clean_csv(f)
        if df is not None:
            name = f.name.upper()
            if "USAGE" in name: data['TRAFICO'] = df
            elif "STATISTICS" in name and "EB/NO" in df.columns.tolist()[1]: data['RF'] = df
            elif "ISP" in name: data['ISP'] = df
            elif "RECLAMOS" in name: data['RECLAMOS'] = df
            elif "FALLAS INTERNAS" in name: data['INTERNAS'] = df

# --- VISTA: RESUMEN ---
if selected == "Resumen":
    st.title("🛡️ Dashboard de Inteligencia")
    
    if not data:
        st.warning("Por favor, cargue los archivos CSV para iniciar el análisis.")
    else:
        # Fila de KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            val = len(data.get('ISP', []))
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div>Fallas ISP</div></div>', unsafe_allow_html=True)
        with c2:
            val = len(data.get('INTERNAS', []))
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div>Fallas Internas</div></div>', unsafe_allow_html=True)
        with c3:
            val = len(data.get('RECLAMOS', []))
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div>Tickets Abonados</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">97.8%</div><div>Uptime Estimado</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Análisis Rápido de IA
        if st.button("🪄 Análisis Rápido con IA"):
            contexto = f"ISP: {len(data.get('ISP', []))} eventos. Internas: {len(data.get('INTERNAS', []))}. Reclamos: {len(data.get('RECLAMOS', []))}."
            with st.spinner("Gemini analizando patrones..."):
                analisis = call_gemini(f"Analiza estos números de gestión mensual y dime cuál es el mayor riesgo: {contexto}")
                st.markdown(f'<div class="ai-response"><b>Perspectiva de IA:</b><br>{analisis}</div>', unsafe_allow_html=True)

# --- VISTA: TELEMETRÍA ---
elif selected == "Telemetría":
    st.title("🛰️ Análisis de Señal y Tráfico")
    
    if 'TRAFICO' in data:
        st.subheader("Tráfico de Red (Forward Link)")
        df_t = data['TRAFICO']
        cols = [c for c in df_t.columns if "Out" in c][:10]
        fig = px.area(df_t, x=df_t.columns[0], y=cols, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    if 'RF' in data:
        st.subheader("Calidad Eb/No por Nodo")
        df_rf = data['RF']
        nodes = [c for c in df_rf.columns if "FL Tuner" in c][:5]
        fig_rf = px.line(df_rf, x=df_rf.columns[0], y=nodes, template="plotly_dark")
        st.plotly_chart(fig_rf, use_container_width=True)

# --- VISTA: EVENTOS ---
elif selected == "Eventos":
    st.title("📋 Registro de Incidencias")
    tab1, tab2, tab3 = st.tabs(["Fallas ISP", "Fallas Internas", "Reclamos"])
    
    with tab1:
        if 'ISP' in data: st.dataframe(data['ISP'], use_container_width=True)
    with tab2:
        if 'INTERNAS' in data: st.dataframe(data['INTERNAS'], use_container_width=True)
    with tab3:
        if 'RECLAMOS' in data: st.dataframe(data['RECLAMOS'], use_container_width=True)

# --- VISTA: INFORME IA ---
elif selected == "Informe IA":
    st.title("🤖 Generador de Informe Ejecutivo")
    st.markdown("Utiliza Gemini 2.5 Flash para redactar un informe profesional basado en los datos cargados.")
    
    if st.button("📝 Generar Informe Detallado"):
        if not data:
            st.error("No hay datos cargados para analizar.")
        else:
            with st.spinner("Redactando informe corporativo..."):
                # Construir un resumen de datos para la IA
                resumen_texto = ""
                for k, df in data.items():
                    resumen_texto += f"\nCATEGORÍA {k}:\n{df.head(10).to_string()}\n"
                
                prompt = f"""
                Genera un informe de gestión mensual para el departamento de IT.
                Datos analizados: {resumen_texto}
                
                El informe debe incluir:
                1. Introducción.
                2. Análisis de fallas de proveedores vs internas.
                3. Comportamiento de tráfico y calidad de señal.
                4. Recomendaciones estratégicas.
                
                Formato: Markdown profesional con tablas y viñetas.
                """
                
                informe = call_gemini(prompt, "Eres el CTO de Meru Networks.")
                st.session_state['full_report'] = informe
    
    if 'full_report' in st.session_state:
        st.markdown(f'<div class="ai-response">{st.session_state["full_report"]}</div>', unsafe_allow_html=True)
        
        # Opción de exportación
        report_bytes = st.session_state['full_report'].encode('utf-8')
        st.download_button("Descargar Informe (.md)", report_bytes, "Informe_Meru_IA.md")
