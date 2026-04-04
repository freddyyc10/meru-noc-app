import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Sistema de Monitoreo",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #007bff;
    }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    .status-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_stdio=True)

# --- FUNCIONES DE PROCESAMIENTO DE DATOS ---

def load_data(file):
    """Carga y limpia el archivo CSV detectando su estructura."""
    content = file.read().decode("utf-8")
    
    # Caso especial: Reporte de Uso (Usage Report) suele tener líneas de encabezado basura
    if "Data Usage Report" in content:
        df = pd.read_csv(io.StringIO(content), skiprows=3)
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
        return df, "USAGE"
    
    # Caso: Estadísticas de iMonitor (Eb/No o Octetos)
    df = pd.read_csv(io.StringIO(content), quotechar='"', skipinitialspace=True)
    
    # Limpieza de nombres de columnas
    df.columns = [c.strip().replace('"', '') for c in df.columns]
    
    if "Date (UTC)" in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Date (UTC)'])
        
        # Determinar si es Eb/No o Octetos
        is_ebno = any("Eb/No" in col for col in df.columns)
        return df, "EBNO" if is_ebno else "STATS"
    
    return df, "UNKNOWN"

# --- SIDEBAR / NAVEGACIÓN ---
st.sidebar.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=80)
st.sidebar.title("NOC Meru Control")
uploaded_files = st.sidebar.file_uploader(
    "Cargar Reportes CSV (iDirect)", 
    type=["csv"], 
    accept_multiple_files=True
)

st.sidebar.markdown("---")
st.sidebar.info("Este sistema procesa reportes de iDirect para monitoreo de niveles de señal y tráfico.")

# --- LÓGICA PRINCIPAL ---
st.title("📡 Dashboard Operativo - VNO Meru Networks")

if not uploaded_files:
    st.warning("⚠️ Por favor, cargue los archivos CSV en el panel lateral para comenzar.")
    
    # Pantalla de inicio visual
    col1, col2, col3 = st.columns(3)
    with col1: st.info("**Eb/No:** Monitoreo de señal RL/FL.")
    with col2: st.info("**Tráfico:** Reporte de consumo en MB.")
    with col3: st.info("**Análisis:** Tendencias y alertas.")
else:
    data_store = {"EBNO": None, "USAGE": None, "STATS": None}
    
    for file in uploaded_files:
        df, dtype = load_data(file)
        data_store[dtype] = df

    # --- SECCIÓN 1: NIVELES DE SEÑAL (EB/NO) ---
    if data_store["EBNO"] is not None:
        df_ebno = data_store["EBNO"]
        st.header("📊 Análisis de Capa Física (Eb/No)")
        
        # Extraer estaciones
        cols = [c for c in df_ebno.columns if "/" in c]
        stations = sorted(list(set([c.split('/')[0] for c in cols])))
        
        selected_st = st.selectbox("Seleccionar Estación para Detalle", stations)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        rl_col = f"{selected_st}/RL Measured Eb/No"
        fl_col = f"{selected_st}/FL Tuner Eb/No"
        
        # Valores actuales
        try:
            current_rl = df_ebno[rl_col].dropna().iloc[-1]
            current_fl = df_ebno[fl_col].dropna().iloc[-1]
            
            with col_m1:
                color = "normal" if current_rl >= 10.5 else "inverse"
                st.metric("Return Link (RL)", f"{current_rl:.2f} dB", delta_color=color)
            with col_m2:
                st.metric("Forward Link (FL)", f"{current_fl:.2f} dB")
            with col_m3:
                status = "🟢 Óptimo" if current_rl > 11 else "🟡 Alerta" if current_rl > 9.5 else "🔴 Crítico"
                st.markdown(f"**Estado de Enlace:**\n### {status}")
        except:
            st.error("No se encontraron datos para la estación seleccionada.")

        # Gráfico de histórico
        fig = go.Figure()
        if rl_col in df_ebno.columns:
            fig.add_trace(go.Scatter(x=df_ebno['Timestamp'], y=df_ebno[rl_col], name="RL (Carga)", line=dict(color='#e74c3c', width=2)))
        if fl_col in df_ebno.columns:
            fig.add_trace(go.Scatter(x=df_ebno['Timestamp'], y=df_ebno[fl_col], name="FL (Descarga)", line=dict(color='#3498db', width=2)))
        
        fig.update_layout(
            title=f"Histórico de Señal: {selected_st}",
            xaxis_title="Fecha/Hora (UTC)",
            yaxis_title="Eb/No (dB)",
            template="plotly_white",
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- SECCIÓN 2: REPORTE DE TRÁFICO (USAGE) ---
    if data_store["USAGE"] is not None:
        st.markdown("---")
        st.header("💾 Consumo de Datos (MB)")
        df_usage = data_store["USAGE"]
        
        # Procesar totales por columna
        # Se asume que la última fila es el total o se calcula
        usage_cols = [c for c in df_usage.columns if " In" in c or " Out" in c]
        
        resumen = []
        for c in df_usage.columns:
            if " In" in c:
                st_name = c.replace(" In", "")
                in_val = pd.to_numeric(df_usage[c], errors='coerce').sum()
                out_col = c.replace(" In", " Out")
                out_val = pd.to_numeric(df_usage[out_col], errors='coerce').sum() if out_col in df_usage.columns else 0
                resumen.append({"Estación": st_name, "In (MB)": in_val, "Out (MB)": out_val, "Total": in_val + out_val})
        
        df_resumen = pd.DataFrame(resumen).sort_values(by="Total", ascending=False)
        
        col_tab, col_chart = st.columns([1, 2])
        with col_tab:
            st.subheader("Top Consumo")
            st.dataframe(df_resumen[['Estación', 'Total']].head(10), use_container_width=True)
            
        with col_chart:
            fig_bar = px.bar(
                df_resumen.head(15), 
                x="Estación", 
                y=["In (MB)", "Out (MB)"],
                title="Top 15 Estaciones - Tráfico Acumulado",
                barmode="group",
                color_discrete_sequence=["#1abc9c", "#34495e"]
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- SECCIÓN 3: ESTADÍSTICAS DE RED (STATS/OCTETOS) ---
    if data_store["STATS"] is not None:
        st.markdown("---")
        st.header("📉 Rendimiento de Red (Octetos)")
        df_stats = data_store["STATS"]
        
        # Filtro rápido de búsqueda
        search = st.text_input("Filtrar estación en estadísticas...")
        stat_cols = [c for c in df_stats.columns if search.lower() in c.lower() and "/" in c]
        
        if stat_cols:
            fig_stats = px.line(df_stats, x="Timestamp", y=stat_cols[:10], # Limitar a 10 para visualización
                               title="Tendencia de Octetos (Muestra)",
                               labels={"value": "Octetos", "variable": "Métrica"})
            st.plotly_chart(fig_stats, use_container_width=True)
        else:
            st.info("Escriba el nombre de una estación para ver sus octetos.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown(f"**NOC Meru Networks** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Estado del Sistema: ONLINE")
