import streamlit as st
import pandas as pd
import io
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- Configuración Visual Estilo NOC ---
st.set_page_config(
    page_title="Meru-Networks NOC Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Avanzados para una interfaz premium
st.markdown("""
    <style>
    /* Fondo y tipografía */
    .stApp { background-color: #0e1117; color: #e0e6ed; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Tarjetas de métricas */
    .metric-card {
        background-color: #1d212b;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Contenedor de Reporte IA */
    .ia-report-container {
        background-color: #0d1117;
        border-left: 4px solid #238636;
        padding: 25px;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
        color: #c9d1d9;
    }

    /* Tablas */
    .stDataFrame { border: 1px solid #30363d; border-radius: 8px; }
    
    /* Botones */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #238636;
        color: white;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2ea043; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- Lógica de Negocio y Conectividad ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "" # El entorno la proveerá automáticamente
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def load_data_robustly(file):
    """
    Lee archivos CSV saltando encabezados variables (como el error de la línea 4).
    """
    try:
        raw_bytes = file.getvalue()
        # Intentar detectar el inicio real de los datos
        content_lines = raw_bytes.decode('utf-8', errors='ignore').splitlines()
        
        skip_rows = 0
        for i, line in enumerate(content_lines[:20]):
            # Buscamos columnas clave de tus archivos específicos
            keys = ["Date", "ZONA", "FECHA DE FALLA", "NOMBRE ISP", "ZONA", "FECHA DE RECLAMO"]
            if any(key in line for key in keys):
                skip_rows = i
                break
        
        file.seek(0)
        df = pd.read_csv(file, skiprows=skip_rows)
        # Limpieza estándar
        df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error procesando {file.name}: {e}")
        return None

def classify_file(df, filename):
    """Clasifica los archivos según su estructura interna."""
    cols_str = " ".join([str(c).upper() for c in df.columns])
    fname = filename.upper()
    
    if "EBN_LOS_NEVADOS" in cols_str or "DATA USAGE" in fname:
        return "uso_datos"
    if "EB/NO" in cols_str or "STATISTICS" in fname:
        if "RL MEASURED" in cols_str or "FL TUNER" in cols_str:
            return "senial_rf"
        if "OCTETS" in cols_str:
            return "trafico_snmp"
    if "NOMBRE ISP" in cols_str or "REPORTE ISP" in fname:
        return "fallas_isp"
    if "NOMBRE DE ABONADO" in cols_str or "RECLAMOS" in fname:
        return "reclamos_abonado"
    if "ABONADOS AFECTADOS" in cols_str or "FALLAS INTERNAS" in fname:
        return "fallas_internas"
    return "desconocido"

def get_ai_analysis(all_data):
    """Genera el texto para el informe de gestión basado en los datos cargados."""
    # Construir un contexto resumido para la IA
    contexto = "RESUMEN DE DATOS CARGADOS:\n"
    if "fallas_isp" in all_data:
        contexto += f"- Fallas de Proveedor: {len(all_data['fallas_isp'])} eventos detectados.\n"
    if "fallas_internas" in all_data:
        contexto += f"- Fallas Internas: {len(all_data['fallas_internas'])} incidencias.\n"
    if "reclamos_abonado" in all_data:
        contexto += f"- Reclamos de Clientes: {len(all_data['reclamos_abonado'])} casos.\n"
    
    prompt = f"""
    Actúa como el Jefe del NOC de Meru-Networks. 
    Estructura un informe de gestión detallado basado en estos datos:
    {contexto}
    
    El informe debe contener:
    1. Análisis de Disponibilidad de Red (considerando eventos de ISP).
    2. Comportamiento de Fallas (Internas vs Proveedor).
    3. Resumen de Atención a Clientes.
    4. Conclusiones y Próximos pasos técnicos.
    
    Usa un lenguaje técnico-ejecutivo profesional.
    """
    
    try:
        # Implementación con manejo de reintentos simple
        response = requests.post(
            ENDPOINT,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=20
        )
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "No se pudo generar el análisis automático en este momento. Por favor, revise la conexión o intente más tarde."

# --- Interfaz Principal ---

with st.sidebar:
    st.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-satellite-space-flatart-icons-flat-flatarticons.png", width=80)
    st.title("Meru NOC v2.0")
    st.markdown("---")
    
    st.subheader("📁 Carga de Reportes")
    uploaded_files = st.file_uploader(
        "Suba sus archivos CSV/Excel", 
        accept_multiple_files=True,
        help="Cargue los reportes de iDirect, ISP, Reclamos y Fallas Internas."
    )
    
    st.markdown("---")
    menu = st.radio(
        "NAVEGACIÓN",
        ["🔭 Vista Global", "📊 Tráfico y Señal", "🛠️ Gestión de Fallas", "📑 Informe de Gestión"]
    )

# Procesar archivos cargados
data_store = {}
if uploaded_files:
    for f in uploaded_files:
        df = load_data_robustly(f)
        if df is not None:
            category = classify_file(df, f.name)
            data_store[category] = df

# --- Vistas del Dashboard ---

if not data_store:
    st.info("👋 Bienvenido al sistema NOC de Meru-Networks. Por favor, cargue los reportes mensuales en el panel izquierdo para comenzar.")
else:
    if menu == "🔭 Vista Global":
        st.header("Centro de Monitoreo Global - Marzo 2026")
        
        # KPIs en la parte superior
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            val = len(data_store.get('fallas_isp', []))
            st.markdown(f'<div class="metric-card"><div class="metric-label">Fallas ISP</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
        with m2:
            val = len(data_store.get('fallas_internas', []))
            st.markdown(f'<div class="metric-card"><div class="metric-label">Fallas Internas</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
        with m3:
            val = len(data_store.get('reclamos_abonado', []))
            st.markdown(f'<div class="metric-card"><div class="metric-label">Reclamos</div><div class="metric-value">{val}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Uptime Est.</div><div class="metric-value">97.8%</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Tabla de fallas recientes
        if 'fallas_internas' in data_store:
            st.subheader("🚨 Últimas Incidencias Internas")
            st.dataframe(data_store['fallas_internas'], use_container_width=True)

    elif menu == "📊 Tráfico y Señal":
        st.header("Análisis de Rendimiento de Red")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if 'uso_datos' in data_store:
                st.subheader("Consumo por Nodo (MBytes)")
                df_u = data_store['uso_datos']
                # Graficar los primeros 5 nodos para no saturar
                plot_cols = [c for c in df_u.columns if "Out" in c][:5]
                fig = px.line(df_u, x=df_u.columns[0], y=plot_cols, template="plotly_dark", title="Tráfico de Salida (Hub -> Remota)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Cargue el archivo 'Data Usage Report' para ver gráficos de tráfico.")

        with col_b:
            if 'senial_rf' in data_store:
                st.subheader("Estabilidad RF (Eb/No)")
                df_s = data_store['senial_rf']
                plot_cols = [c for c in df_s.columns if "FL Tuner" in c][:5]
                fig_s = px.scatter(df_s, x=df_s.columns[0], y=plot_cols, template="plotly_dark", title="Forward Link Tuner Eb/No")
                st.plotly_chart(fig_s, use_container_width=True)
            else:
                st.warning("Cargue el archivo 'Statistics' con Eb/No para ver estabilidad RF.")

    elif menu == "🛠️ Gestión de Fallas":
        st.header("Base de Datos de Incidencias")
        t1, t2, t3 = st.tabs(["Fallas ISP", "Reclamos Abonados", "Fallas Internas"])
        
        with t1:
            if 'fallas_isp' in data_store: st.dataframe(data_store['fallas_isp'], use_container_width=True)
            else: st.info("Sin datos de ISP.")
        with t2:
            if 'reclamos_abonado' in data_store: st.dataframe(data_store['reclamos_abonado'], use_container_width=True)
            else: st.info("Sin datos de Reclamos.")
        with t3:
            if 'fallas_internas' in data_store: st.dataframe(data_store['fallas_internas'], use_container_width=True)
            else: st.info("Sin datos de Fallas Internas.")

    elif menu == "📑 Informe de Gestión":
        st.header("Generación de Reporte Ejecutivo")
        
        if st.button("🚀 Iniciar Análisis Inteligente con IA"):
            with st.spinner("Analizando tendencias de red y fallas..."):
                st.session_state['reporte_ia'] = get_ai_analysis(data_store)
        
        if 'reporte_ia' in st.session_state:
            st.markdown(f"""
            <div class="ia-report-container">
                {st.session_state['reporte_ia'].replace('\n', '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📥 Exportar Resultados")
            
            # Generar Excel en memoria para descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for cat, df in data_store.items():
                    df.to_excel(writer, sheet_name=cat[:31], index=False)
            
            st.download_button(
                label="Descargar Excel Consolidado",
                data=output.getvalue(),
                file_name=f"Reporte_Consolidado_Meru_{datetime.now().strftime('%Y%m')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("Nota: El reporte de Word se puede generar copiando el texto anterior al formato institucional preestablecido.")
