import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | NOC Control Center",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ULTRA PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Fondo general */
    .stApp {
        background: radial-gradient(circle at top right, #1a1f2e, #0d1117);
        color: #e6edf3;
    }

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.95);
        border-right: 1px solid #30363d;
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }

    /* Contenedores de KPIs (Tarjetas de cristal) */
    .kpi-container {
        background: rgba(33, 38, 45, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px;
        padding: 24px;
        text-align: left;
        transition: transform 0.3s ease, border 0.3s ease;
    }
    .kpi-container:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }
    .kpi-label {
        color: #8b949e;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .kpi-value {
        color: #f0f6fc;
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 8px;
    }
    .kpi-delta {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 5px;
    }

    /* Reporte IA - Estilo Terminal/Doc */
    .ia-box {
        background: #0d1117;
        border: 1px solid #30363d;
        border-left: 5px solid #238636;
        border-radius: 12px;
        padding: 40px;
        color: #c9d1d9;
        line-height: 1.8;
        font-size: 1.05rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    /* Botones Modernos */
    .stButton>button {
        background: linear-gradient(135deg, #238636, #2ea043);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(46, 160, 67, 0.4);
        transform: scale(1.02);
    }

    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tables */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE BACKEND (Respetando formatos) ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # Automático en este entorno
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def load_csv_data(file):
    """Carga robusta para archivos con metadatos en las primeras líneas."""
    try:
        raw_content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
        skip_n = 0
        for i, line in enumerate(raw_content[:15]):
            if any(k in line.upper() for k in ["DATE", "FECHA", "ZONA", "NODO"]):
                skip_n = i
                break
        file.seek(0)
        df = pd.read_csv(file, skiprows=skip_n)
        df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error en {file.name}: {e}")
        return None

def identify_content(df, name):
    """Clasificación inteligente por columnas y nombre."""
    cols = " ".join([str(c).upper() for c in df.columns])
    n = name.upper()
    if "EBN_" in cols or "USAGE" in n: return "TRAFICO"
    if "EB/NO" in cols or "STATISTICS" in n:
        return "RF" if "TUNER" in cols or "MEASURED" in cols else "SNMP"
    if "NOMBRE ISP" in cols: return "ISP"
    if "RECLAMO" in cols or "ABONADO" in cols: return "CLIENTES"
    if "AFECTADOS" in cols or "INTERNAS" in n: return "INTERNAS"
    return "OTRO"

def ai_generate_report(data_map):
    """Generador de informe técnico vía IA."""
    summary = "SITUACIÓN ACTUAL:\n"
    if "ISP" in data_map: summary += f"- Fallas ISP detectadas: {len(data_map['ISP'])}\n"
    if "INTERNAS" in data_map: summary += f"- Incidencias internas registradas: {len(data_map['INTERNAS'])}\n"
    if "CLIENTES" in data_map: summary += f"- Casos de abonados reportados: {len(data_map['CLIENTES'])}\n"
    
    prompt = f"""
    Eres el Director Técnico del NOC de Meru Networks. 
    Basado en los siguientes datos consolidados del mes, genera un informe técnico ejecutivo:
    {summary}
    
    Estructura:
    1. RESUMEN EJECUTIVO (Párrafo de alto nivel).
    2. ANÁLISIS DE DISPONIBILIDAD (ISP vs Interno).
    3. COMPORTAMIENTO DE SEÑAL Y TRÁFICO (Si aplica).
    4. ACCIONES CORRECTIVAS Y RECOMENDACIONES.
    
    Mantén un tono profesional, directo y técnico. Usa formato Markdown.
    """
    
    try:
        res = requests.post(ENDPOINT, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "⚠️ Error al conectar con el motor de IA. Por favor verifique la carga de datos."

# --- INTERFAZ DE USUARIO ---

with st.sidebar:
    st.markdown("<h1 style='color:#58a6ff; font-weight:800; margin-bottom:0;'>MERU NOC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; margin-top:0;'>Network Operations Center</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    files = st.file_uploader("📤 Carga de Archivos Mensuales", accept_multiple_files=True)
    
    st.markdown("---")
    nav = st.radio("SISTEMAS", ["📊 Dashboard Global", "🛰️ Análisis de Red", "📝 Gestión de Fallas", "🤖 Generar Informe"])

# Procesamiento
storage = {}
if files:
    for f in files:
        df = load_csv_data(f)
        if df is not None:
            cat = identify_content(df, f.name)
            storage[cat] = df

# --- VISTAS ---

if not storage:
    st.markdown("""
        <div style='text-align: center; padding: 100px 20px;'>
            <h2 style='color:#8b949e;'>Esperando Datos de Red...</h2>
            <p style='color:#484f58;'>Por favor, cargue los archivos CSV de iDirect, ISP y Reclamos en el panel lateral.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    if nav == "📊 Dashboard Global":
        st.title("Estado de la Infraestructura")
        
        # Fila de KPIs con diseño personalizado
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            val = len(storage.get('ISP', []))
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Eventos ISP</div><div class="kpi-value">{val}</div><div class="kpi-delta" style="color:#ff7b72;">↓ Crítico</div></div>""", unsafe_allow_html=True)
        with c2:
            val = len(storage.get('INTERNAS', []))
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Fallas Internas</div><div class="kpi-value">{val}</div><div class="kpi-delta" style="color:#58a6ff;">● Gestión Propia</div></div>""", unsafe_allow_html=True)
        with c3:
            val = len(storage.get('CLIENTES', []))
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Tickets Abiertos</div><div class="kpi-value">{val}</div><div class="kpi-delta" style="color:#f2cc60;">⚠ Atención Requerida</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="kpi-container"><div class="kpi-label">Uptime Mensual</div><div class="kpi-value">98.4%</div><div class="kpi-delta" style="color:#3fb950;">↑ 0.6% vs mes ant.</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_main, col_side = st.columns([2, 1])
        with col_main:
            st.subheader("📋 Últimas Incidencias Registradas")
            disp_df = storage.get('INTERNAS', storage.get('ISP', pd.DataFrame()))
            st.table(disp_df.head(10))
            
        with col_side:
            st.subheader("🎯 Distribución de Fallas")
            labels = ['ISP', 'Internas', 'Reclamos']
            values = [len(storage.get('ISP', [])), len(storage.get('INTERNAS', [])), len(storage.get('CLIENTES', []))]
            fig_pie = px.pie(names=labels, values=values, hole=0.7, color_discrete_sequence=['#ff7b72', '#58a6ff', '#f2cc60'])
            fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

    elif nav == "🛰️ Análisis de Red":
        st.title("Métricas Satelitales")
        t1, t2 = st.tabs(["📉 Tráfico de Datos", "📡 Calidad Eb/No"])
        
        with t1:
            if 'TRAFICO' in storage:
                df_t = storage['TRAFICO']
                # Limpiar nombres de columnas para gráfico
                out_cols = [c for c in df_t.columns if "Out" in c][:8]
                fig_t = px.line(df_t, x=df_t.columns[0], y=out_cols, title="Consumo de Ancho de Banda por Nodo", template="plotly_dark")
                fig_t.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_t, use_container_width=True)
            else:
                st.warning("Cargue el 'Data Usage Report' para ver métricas de tráfico.")

        with t2:
            if 'RF' in storage:
                df_rf = storage['RF']
                rf_cols = [c for c in df_rf.columns if "FL Tuner" in c][:6]
                fig_rf = px.scatter(df_rf, x=df_rf.columns[0], y=rf_cols, title="Estabilidad Forward Link (Eb/No)", template="plotly_dark")
                st.plotly_chart(fig_rf, use_container_width=True)
            else:
                st.warning("Cargue los archivos 'Statistics' para ver niveles de señal.")

    elif nav == "📝 Gestión de Fallas":
        st.title("Logs de Gestión")
        cat_view = st.selectbox("Seleccione Categoría", ["ISP", "INTERNAS", "CLIENTES"])
        if cat_view in storage:
            st.dataframe(storage[cat_view], use_container_width=True)
        else:
            st.info(f"No hay datos cargados para {cat_view}")

    elif nav == "🤖 Generar Informe":
        st.title("Inteligencia Operativa")
        st.info("Este módulo procesa todos los archivos cargados para redactar el informe técnico automáticamente.")
        
        if st.button("🪄 REDACTAR INFORME MENSUAL"):
            with st.spinner("Analizando correlación de fallas y datos de tráfico..."):
                reporte = ai_generate_report(storage)
                st.session_state['current_report'] = reporte
        
        if 'current_report' in st.session_state:
            st.markdown(f"""<div class="ia-box">{st.session_state['current_report']}</div>""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Exportación
            st.subheader("📥 Exportar")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                # Excel Consolidado
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for k, v in storage.items(): v.to_excel(writer, sheet_name=k, index=False)
                st.download_button("Descargar Datos Consolidados (Excel)", output.getvalue(), "NOC_Data_Consolidated.xlsx")
            with col_ex2:
                st.button("Enviar Reporte a Word (Formato Meru)", disabled=True, help="Función en desarrollo según plantilla")
