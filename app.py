import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Meru NOC - Gestión Integral", layout="wide", page_icon="📡")

def limpiar_dataframe(df):
    """Limpia filas vacías iniciales y normaliza columnas"""
    if df is None: return None
    # Eliminar filas donde todo es NaN
    df = df.dropna(how='all').reset_index(drop=True)
    # Si la primera fila parece ser basura o título, buscar el encabezado real
    if df.iloc[0].isnull().sum() > len(df.columns) / 2:
        df.columns = df.iloc[1]
        df = df[2:].reset_index(drop=True)
    
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

def procesar_csv(file):
    if file is not None:
        # Leemos el archivo intentando detectar el separador
        try:
            content = file.getvalue().decode('utf-8')
            df = pd.read_csv(io.StringIO(content), sep=None, engine='python')
            return limpiar_dataframe(df)
        except Exception as e:
            st.error(f"Error al procesar archivo: {e}")
    return None

# --- UI PRINCIPAL ---
st.title("🛰️ Meru-Networks NOC: Dashboard de Operaciones")
st.markdown("---")

# --- SIDEBAR: CARGA DE DATOS ---
st.sidebar.image("https://img.icons8.com/fluency/96/network.png", width=80)
st.sidebar.header("📥 Carga de Datos Mensual")

file_fallas = st.sidebar.file_uploader("1. Fallas Internas (CSV)", type=['csv'])
file_isp = st.sidebar.file_uploader("2. Reporte ISP (CSV)", type=['csv'])
file_reclamos = st.sidebar.file_uploader("3. Reclamos Abonados (CSV)", type=['csv'])

# --- PROCESAMIENTO ---
df_fallas = procesar_csv(file_fallas)
df_isp = procesar_csv(file_isp)
df_reclamos = procesar_csv(file_reclamos)

if df_fallas is not None and df_reclamos is not None:
    # 1. ANÁLISIS DE TICKETS (Gestor de Tickets)
    # Identificar columnas de cierre (ajustar según tus nombres reales)
    col_cierre = [c for c in df_reclamos.columns if 'CIERRE' in c or 'SOLUCION' in c]
    if col_cierre:
        df_reclamos['ESTATUS'] = df_reclamos[col_cierre[0]].apply(lambda x: 'CERRADO' if pd.notnull(x) and str(x).strip() != '' else 'ABIERTO')
    else:
        df_reclamos['ESTATUS'] = 'PENDIENTE'

    tickets_abiertos = df_reclamos[df_reclamos['ESTATUS'] == 'ABIERTO']
    tickets_cerrados = df_reclamos[df_reclamos['ESTATUS'] == 'CERRADO']

    # 2. ANÁLISIS DE DISPONIBILIDAD (Estimación basada en fallas)
    total_fallas_internas = len(df_fallas)
    total_fallas_isp = len(df_isp) if df_isp is not None else 0
    total_eventos = total_fallas_internas + total_fallas_isp
    
    # Cálculo ficticio de disponibilidad (ejemplo: basado en horas del mes)
    horas_mes = 720
    # Intentar extraer duración si existe columna DURACIÓN
    col_duracion = [c for c in df_fallas.columns if 'DURACI' in c]
    # (Aquí podrías sumar las duraciones reales si el formato es HH:MM:SS)
    disponibilidad = 100 - (total_eventos * 0.15) # Factor de corrección simple para el demo

    # --- DASHBOARD ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tickets Abiertos", len(tickets_abiertos), delta_color="inverse")
    m2.metric("Tickets Cerrados", len(tickets_cerrados))
    m3.metric("Fallas ISP", total_fallas_isp)
    m4.metric("Disponibilidad Red", f"{disponibilidad:.2f}%")

    st.markdown("### 📋 Gestor de Tickets Recientes")
    st.dataframe(df_reclamos[['ZONA', 'NOMBRE DE ABONADO', 'TIPO DE RECLAMO', 'ESTATUS']].head(10), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.sunburst(df_reclamos, path=['ESTATUS', 'TIPO DE RECLAMO'], title="Estructura de Casos")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_b:
        # Análisis de Fallas Internas por Tipo
        col_t_falla = [c for c in df_fallas.columns if 'TIPO' in c]
        if col_t_falla:
            fig_bar = px.bar(df_fallas[col_t_falla[0]].value_counts(), title="Tipología de Fallas Internas", labels={'value':'Cantidad', 'index':'Falla'})
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- GENERADOR DE REPORTES WHATSAPP ---
    st.markdown("---")
    st.subheader("📲 Generador de Reportes WhatsApp")
    
    # Detección de mes
    mes_ref = "MARZO 2026" # Por defecto
    col_fecha = [c for c in df_reclamos.columns if 'FECHA' in c]
    if col_fecha:
        try:
            sample_date = pd.to_datetime(df_reclamos[col_fecha[0]].iloc[0])
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_ref = f"{meses[sample_date.month-1].upper()} {sample_date.year}"
        except: pass

    reporte_wa = f"""*REPORTE NOC MERU-NETWORKS* 📡
*Periodo:* {mes_ref}

✅ *Disponibilidad de Red:* {disponibilidad:.2f}%
⚠️ *Eventos ISP:* {total_fallas_isp}
🔧 *Fallas Internas:* {total_fallas_internas}

🎫 *Gestión de Tickets:*
• Total Recibidos: {len(df_reclamos)}
• Casos Cerrados: {len(tickets_cerrados)}
• Casos en Proceso: {len(tickets_abiertos)}

*Estatus Tickets Abiertos:*
{chr(10).join([f"- {row['NOMBRE DE ABONADO']}: {row['TIPO DE RECLAMO']}" for _, row in tickets_abiertos.head(5).iterrows()])}

_Generado por Sistema de Gestión de Operaciones Meru_"""

    st.text_area("Copiar para WhatsApp:", reporte_wa, height=300)
    
    if st.button("📥 Descargar Reporte Consolidado (Excel)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_reclamos.to_excel(writer, sheet_name='Tickets', index=False)
            df_fallas.to_excel(writer, sheet_name='Fallas_Internas', index=False)
            if df_isp is not None: df_isp.to_excel(writer, sheet_name='ISP', index=False)
        st.download_button("Click para descargar", output.getvalue(), f"Reporte_NOC_{mes_ref}.xlsx")

else:
    # Pantalla de bienvenida
    st.info("👋 Bienvenida/o. Por favor, cargue los 3 archivos CSV en el panel izquierdo para iniciar el análisis del mes.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 1. Fallas Internas")
        st.write("Analiza cortes de energía, problemas de RF y errores de configuración propios.")
    with col2:
        st.markdown("### 2. Reporte ISP")
        st.write("Registra eventos de Sun Outage, Rain Fade y mantenimientos del proveedor satelital.")
        st.markdown("### 2. Reporte ISP")
        st.write("Registra eventos de Sun Outage, Rain Fade y mantenimientos del proveedor satelital.")
    with col3:
        st.markdown("### 3. Reclamos")
        st.write("Gestor de tickets de abonados para medir el SLA de atención final.")
