import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la interfaz
st.set_page_config(page_title="VNO Meru NOC", layout="wide", page_icon="📡")

# Estilos personalizados para mejorar la visibilidad
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_stdio=True)

st.title("📡 Dashboard de Monitoreo - VNO Meru")
st.info("Cargue los reportes de iDirect (Statistics y Usage) para visualizar el estado de la red.")

# Sidebar para carga de datos
st.sidebar.header("Panel de Control")
ebno_file = st.sidebar.file_uploader("1. Reporte Eb/No (Statistics CSV)", type=["csv"])
usage_file = st.sidebar.file_uploader("2. Reporte de Tráfico (Usage CSV)", type=["csv"])

def parse_ebno_data(file):
    """Procesa el CSV de estadísticas de Eb/No."""
    # Leemos el CSV limpiando las comillas automáticamente
    df = pd.read_csv(file, quotechar='"', skipinitialspace=True)
    
    # La primera columna suele ser la fecha
    df.rename(columns={df.columns[0]: 'Timestamp'}, inplace=True)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Extraer nombres de estaciones únicos (Formato: ESTACION/Metrica)
    available_cols = [c for c in df.columns if '/' in c]
    stations = sorted(list(set([c.split('/')[0] for c in available_cols])))
    
    return df, stations

def parse_usage_data(file):
    """Procesa el CSV de reporte de consumo de datos."""
    # Estos reportes suelen tener 3 líneas de encabezado antes de los datos
    df = pd.read_csv(file, skiprows=3)
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    return df

# LÓGICA DE VISUALIZACIÓN EB/NO
if ebno_file:
    try:
        df_ebno, stations = parse_ebno_data(ebno_file)
        
        st.subheader("📊 Análisis de Niveles de Señal (Eb/No)")
        col_selector, col_metrics = st.columns([1, 3])
        
        with col_selector:
            selected_station = st.selectbox("Seleccione una Estación", stations)
            
            # Identificar columnas específicas
            rl_col = f"{selected_station}/RL Measured Eb/No"
            fl_col = f"{selected_station}/FL Tuner Eb/No"
            
            # Obtener último valor disponible (ignorando nulos)
            try:
                last_data = df_ebno.dropna(subset=[rl_col, fl_col]).iloc[-1]
                val_rl = float(last_data[rl_col])
                val_fl = float(last_data[fl_col])
                
                # Mostrar métricas con colores de alerta
                st.metric("Return Link (RL)", f"{val_rl:.2f} dB")
                if val_rl < 9.0:
                    st.error(f"⚠️ RL Crítico en {selected_station}")
                elif val_rl < 10.5:
                    st.warning(f"🔔 RL Bajo en {selected_station}")
                
                st.metric("Forward Link (FL)", f"{val_fl:.2f} dB")
            except:
                st.warning("No hay datos recientes para esta estación.")

        with col_metrics:
            # Gráfico de líneas dinámico
            fig = go.Figure()
            
            if rl_col in df_ebno.columns:
                fig.add_trace(go.Scatter(x=df_ebno['Timestamp'], y=df_ebno[rl_col], 
                                         name="RL Measured", line=dict(color='#FF4B4B')))
            if fl_col in df_ebno.columns:
                fig.add_trace(go.Scatter(x=df_ebno['Timestamp'], y=df_ebno[fl_col], 
                                         name="FL Tuner", line=dict(color='#1C83E1')))
                
            fig.update_layout(
                title=f"Histórico Eb/No - {selected_station}",
                xaxis_title="Tiempo (UTC)",
                yaxis_title="dB",
                hovermode="x unified",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al procesar archivo de niveles: {e}")

# LÓGICA DE VISUALIZACIÓN TRÁFICO
if usage_file:
    st.markdown("---")
    st.subheader("💾 Consumo de Datos por Estación")
    try:
        df_usage = parse_usage_data(usage_file)
        # Tomamos la última fila que suele contener el acumulado del reporte
        totals = df_usage.iloc[-1]
        
        usage_summary = []
        for col in df_usage.columns:
            if " In" in col:
                st_name = col.replace(" In", "")
                val_in = totals[col]
                out_col = col.replace(" In", " Out")
                val_out = totals[out_col] if out_col in df_usage.columns else 0
                
                usage_summary.append({
                    "Estación": st_name,
                    "Carga (In)": float(val_in),
                    "Descarga (Out)": float(val_out),
                    "Total MB": float(val_in) + float(val_out)
                })
        
        df_plot = pd.DataFrame(usage_summary).sort_values(by="Total MB", ascending=False).head(20)
        
        fig_usage = px.bar(
            df_plot, 
            x="Estación", 
            y=["Carga (In)", "Descarga (Out)"],
            title="Top 20 Estaciones con Mayor Tráfico (MB)",
            labels={"value": "MegaBytes", "variable": "Dirección"},
            color_discrete_sequence=["#00D2D3", "#54A0FF"]
        )
        st.plotly_chart(fig_usage, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al procesar archivo de tráfico: {e}")

if not ebno_file and not usage_file:
    st.write("👈 Use el panel lateral para subir los archivos `.csv` exportados del iMonitor.")
