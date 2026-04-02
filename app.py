import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru NOC - Dashboard Dinámico", layout="wide", page_icon="📡")

# Estilos profesionales
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        border-left: 5px solid #004488; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    .report-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #004488; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def extraer_periodo(df, col_fecha):
    """Detecta el mes y año predominante en los datos cargados"""
    try:
        fechas = pd.to_datetime(df[col_fecha], errors='coerce').dropna()
        if not fechas.empty:
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                     "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_num = fechas.dt.month.mode()[0]
            anio = fechas.dt.year.mode()[0]
            return f"{meses[mes_num-1]} {anio}"
    except:
        pass
    return None

def cargar_datos(label, skip=0):
    uploaded_file = st.sidebar.file_uploader(label, type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, skiprows=skip, sep=None, engine='python')
            df = df.dropna(how='all', axis=0)
            df.columns = [c.strip().upper() for c in df.columns]
            return df
        except Exception as e:
            st.sidebar.error(f"Error en {label}: {e}")
    return None

# --- SIDEBAR ---
st.sidebar.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=80)
st.sidebar.header("📥 Carga de Archivos")

df_fallas = cargar_datos("1. Fallas Internas", skip=3)
df_isp = cargar_datos("2. Reporte ISP", skip=3)
df_reclamos = cargar_datos("3. Reclamos Abonados", skip=4)

# Selección manual de mes por si la detección falla o el usuario quiere cambiarlo
st.sidebar.divider()
st.sidebar.subheader("⚙️ Configuración del Reporte")
mes_manual = st.sidebar.selectbox("Mes del Reporte", 
    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    index=datetime.now().month - 1)
anio_manual = st.sidebar.number_input("Año", min_value=2024, max_value=2030, value=2026)

# --- LÓGICA DE PERIODO DINÁMICO ---
periodo_reporte = f"{mes_manual} {anio_manual}"
if df_reclamos is not None:
    # Intentar detectar automáticamente el mes del archivo
    col_fecha_rec = [c for c in df_reclamos.columns if 'FECHA' in c]
    if col_fecha_rec:
        detec = extraer_periodo(df_reclamos, col_fecha_rec[0])
        if detec: periodo_reporte = detec

# --- CABECERA DINÁMICA ---
col_1, col_2 = st.columns([1, 5])
with col_2:
    st.title("📡 Meru-Networks: Sistema NOC")
    st.markdown(f"#### Reporte de Operaciones | Periodo: **{periodo_reporte}**")

st.divider()

if df_fallas is not None and df_reclamos is not None:
    # KPIs
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Reclamos", len(df_reclamos), periodo_reporte)
    with m2:
        st.metric("Fallas Internas", len(df_fallas))
    with m3:
        n_isp = len(df_isp) if df_isp is not None else 0
        st.metric("Eventos ISP", n_isp)
    with m4:
        st.metric("SLA Estimado", "97.5%")

    # GRÁFICOS
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.write("📍 **Distribución por Zona**")
        col_zona = [c for c in df_reclamos.columns if 'ZONA' in c or 'ESTADO' in c]
        if col_zona:
            fig = px.pie(df_reclamos, names=col_zona[0], hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.write("🛠️ **Tipos de Falla más Frecuentes**")
        col_tipo = [c for c in df_fallas.columns if 'TIPO' in c]
        if col_tipo:
            data_bar = df_fallas[col_tipo[0]].value_counts().reset_index()
            fig_bar = px.bar(data_bar, x=col_tipo[0], y='count', color=col_tipo[0], template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # REPORTES
    st.subheader("📝 Entregables Automáticos")
    t1, t2 = st.tabs(["📱 WhatsApp", "📥 Exportar"])
    
    with t1:
        msg = f"*MERU-NETWORKS: REPORTE NOC {periodo_reporte.upper()}*\n\n" \
              f"📊 *Métricas:*\n" \
              f"• Reclamos: {len(df_reclamos)}\n" \
              f"• Fallas: {len(df_fallas)}\n" \
              f"• ISP: {n_isp}\n\n" \
              f"Generado automáticamente por sistema Meru-App."
        st.text_area("Copia el reporte:", msg, height=150)

    with t2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_fallas.to_excel(writer, sheet_name='Fallas', index=False)
            df_reclamos.to_excel(writer, sheet_name='Reclamos', index=False)
        st.download_button("Descargar Excel", output.getvalue(), f"Reporte_NOC_{periodo_reporte}.xlsx")

else:
    st.info(f"💡 **Listo para trabajar:** Cargue los archivos de cualquier mes (Enero, Febrero, {periodo_reporte}, etc.) para generar el reporte automáticamente.")
