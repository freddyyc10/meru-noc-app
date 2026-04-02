import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru NOC - Dashboard Marzo 2026", layout="wide", page_icon="📡")

# Estilos personalizados para un look profesional (Blue Corporate)
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
    .stButton>button { 
        background-color: #004488; 
        color: white; 
        border-radius: 8px; 
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
col_1, col_2 = st.columns([1, 5])
with col_2:
    st.title("📡 Meru-Networks: Sistema de Gestión NOC")
    st.markdown("#### Reporte Mensual de Operaciones | Mes de Referencia: **Marzo 2026**")
    st.info("Cargue los archivos CSV generados para visualizar las métricas de este mes.")

st.divider()

# --- SIDEBAR: GESTIÓN DE ARCHIVOS ---
st.sidebar.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=80)
st.sidebar.header("📥 Carga de Datos")

def cargar_datos(label, skip=0):
    uploaded_file = st.sidebar.file_uploader(label, type=['csv'])
    if uploaded_file is not None:
        try:
            # Leer CSV detectando el delimitador automáticamente
            df = pd.read_csv(uploaded_file, skiprows=skip, sep=None, engine='python')
            df = df.dropna(how='all', axis=0) # Eliminar filas vacías
            df.columns = [c.strip().upper() for c in df.columns] # Limpiar nombres de columnas
            return df
        except Exception as e:
            st.sidebar.error(f"Error en {label}: {e}")
    return None

# Carga con saltos de línea basados en la estructura de tus archivos subidos
df_fallas = cargar_datos("1. Fallas Internas (CSV)", skip=3)
df_isp = cargar_datos("2. Reporte ISP (CSV)", skip=3)
df_reclamos = cargar_datos("3. Reclamos Abonados (CSV)", skip=4)
df_vno = cargar_datos("4. Tráfico VNO (CSV)", skip=0)

# --- PROCESAMIENTO Y DASHBOARD ---
if df_fallas is not None and df_reclamos is not None:
    
    # KPIs SUPERIORES
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Reclamos", len(df_reclamos), f"Marzo 2026")
    with m2:
        st.metric("Fallas de Red", len(df_fallas), "Internas")
    with m3:
        n_isp = len(df_isp) if df_isp is not None else 0
        st.metric("Afectación ISP", n_isp, "Proveedores")
    with m4:
        st.metric("SLA Objetivo", "97.8%", "Disponibilidad")

    st.subheader("📊 Análisis de Incidencias y Soporte")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.write("**Distribución Geográfica de Reclamos**")
        # Columna ZONA detectada en tu archivo
        if 'ZONA' in df_reclamos.columns:
            fig_pie = px.pie(df_reclamos, names='ZONA', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.write("**Fallas por Categoría (Soporte Técnico)**")
        # Columna TIPO DE FALLA detectada
        col_tipo = [c for c in df_fallas.columns if 'TIPO' in c][0]
        fig_bar = px.bar(df_fallas[col_tipo].value_counts().reset_index(), x=col_tipo, y='count', 
                        labels={'count': 'Cantidad'}, color=col_tipo, template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- SECCIÓN DE REPORTES AUTOMÁTICOS ---
    st.divider()
    st.subheader("📝 Generación de Entregables")
    
    t1, t2, t3 = st.tabs(["📱 WhatsApp Ejecutivo", "📑 Resumen de Gestión", "📥 Exportar Excel"])

    with t1:
        # Generar mensaje dinámico para WhatsApp
        msg = f"""*MERU-NETWORKS: REPORTE NOC MARZO 2026* 📡

📊 *Métricas del Mes:*
• Disponibilidad: 97.8%
• Reclamos Abonados: {len(df_reclamos)}
• Fallas Internas: {len(df_fallas)}
• Eventos ISP: {n_isp}

⚠️ *Nodos Críticos / Novedades:*
1. Sun Outage (Equinoccio) afectó estabilidad del Hub.
2. BAR27 (Nutrias) presenta fallas intermitentes de energía.
3. Se requiere mantenimiento preventivo en MIR55.

*Ing. Freddy Coronado*"""
        st.text_area("Mensaje listo para copiar:", msg, height=250)
        st.caption("Copia este mensaje y envíalo al grupo de Operaciones.")

    with t2:
        st.markdown(f"""
        ### Informe de Gestión Mensual
        **Periodo:** Marzo 2026  
        **Responsable:** Ing. Freddy Coronado
        
        - Se atendieron **{len(df_reclamos)}** requerimientos de usuarios finales.
        - Se registraron **{len(df_fallas)}** fallas de infraestructura propia (Energía/RF).
        - La causa principal de reclamos este mes fue: *{df_reclamos['TIPO DE RECLAMO '].mode()[0]}*.
        - La zona con mayor actividad de soporte fue: *{df_reclamos['ZONA'].mode()[0]}*.
        """)

    with t3:
        # Generar Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_fallas.to_excel(writer, sheet_name='Fallas_Internas', index=False)
            df_reclamos.to_excel(writer, sheet_name='Reclamos_Abonados', index=False)
            if df_isp is not None: df_isp.to_excel(writer, sheet_name='Reporte_ISP', index=False)
        
        st.download_button(
            label="Descargar Reporte Consolidado (Excel)",
            data=output.getvalue(),
            file_name="Reporte_Consolidado_MERU_MARZO_2026.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("⚠️ **Esperando Datos:** Por favor cargue los archivos CSV en el panel de la izquierda para generar el análisis de Marzo.")
    # Imagen de espera decorativa
    st.image("https://img.freepik.com/free-vector/data-report-concept-illustration_114360-883.jpg", width=400)
