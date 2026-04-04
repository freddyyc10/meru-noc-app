import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Data Analysis",
    page_icon="📡",
    layout="wide"
)

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    h1, h2, h3 { color: #1e293b; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CARGA ---

def clean_csv_header(file):
    """Detecta el inicio real de los datos y devuelve un DataFrame limpio."""
    content = file.getvalue().decode('utf-8').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        # Buscamos el encabezado que contiene 'Date' o nombres de estaciones con '/'
        if "Date" in line or "/" in line or "Octets" in line:
            skip_rows = i
            break
    
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip_rows)
    # Limpiar espacios en los nombres de las columnas
    df.columns = [c.strip() for c in df.columns]
    return df

def get_stations_from_usage(df):
    """Extrae nombres únicos de estaciones de columnas tipo 'Station / In Octets'."""
    stations = set()
    for col in df.columns:
        if " / " in col:
            stations.add(col.split(" / ")[0].strip())
    return sorted(list(stations))

# --- PROCESAMIENTO DE CONSUMO (DATA USAGE) ---

def process_usage_report(df):
    st.header("💾 Análisis de Consumo de Datos")
    
    stations = get_stations_from_usage(df)
    if not stations:
        st.error("No se detectaron columnas con el formato 'Estación / In Octets' o similar.")
        return

    usage_data = []
    
    for st_name in stations:
        # Identificar columnas de entrada y salida
        in_col = next((c for c in df.columns if st_name in c and "In" in c), None)
        out_col = next((c for c in df.columns if st_name in c and "Out" in c), None)
        
        if in_col and out_col:
            # Convertir a numérico (Octetos a MB)
            val_in = pd.to_numeric(df[in_col], errors='coerce').sum() / (1024 * 1024)
            val_out = pd.to_numeric(df[out_col], errors='coerce').sum() / (1024 * 1024)
            
            if (val_in + val_out) > 0:
                usage_data.append({
                    "Estación": st_name,
                    "Descarga (MB)": round(val_in, 2),
                    "Subida (MB)": round(val_out, 2),
                    "Total (MB)": round(val_in + val_out, 2)
                })

    if usage_data:
        res_df = pd.DataFrame(usage_data).sort_values("Total (MB)", ascending=False)
        
        # Métricas Globales
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Tráfico (MB)", f"{res_df['Total (MB)'].sum():,.2f}")
        c2.metric("Estación con más Tráfico", res_df.iloc[0]['Estación'])
        c3.metric("Promedio por Estación", f"{res_df['Total (MB)'].mean():,.2f} MB")

        col_left, col_right = st.columns([1.5, 1])
        
        with col_left:
            fig = px.bar(res_df.head(15), 
                         x='Total (MB)', 
                         y='Estación', 
                         orientation='h',
                         title="Top 15 Estaciones por Consumo Total",
                         color='Total (MB)',
                         color_continuous_scale='Blues')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.subheader("Detalle por Estación")
            st.dataframe(res_df, hide_index=True, use_container_width=True)
            
            csv = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte Limpio", csv, "reporte_consumo_meru.csv", "text/csv")
    else:
        st.warning("El archivo no contiene datos de consumo válidos (sumatoria cero).")

# --- PROCESAMIENTO DE EB/NO ---

def process_ebno_report(df):
    st.header("📶 Análisis de Señal (Eb/No)")
    
    # Intentar detectar columna de fecha
    date_col = next((c for c in df.columns if "Date" in c or "Timestamp" in c), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    stations = []
    for c in df.columns:
        if "/" in c: stations.append(c.split("/")[0].strip())
    stations = sorted(list(set(stations)))

    selected = st.selectbox("Seleccionar Estación para Gráfico Temporal", stations)
    
    # Buscar FL (Forward) y RL (Return)
    fl_col = next((c for c in df.columns if selected in c and ("FL" in c or "In" in c)), None)
    rl_col = next((c for c in df.columns if selected in c and ("RL" in c or "Out" in c)), None)

    if fl_col and rl_col:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[fl_col], name="Señal FL (dB)"))
        fig.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[rl_col], name="Señal RL (dB)"))
        fig.update_layout(title=f"Histórico de Señal: {selected}", hovermode="x", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Seleccione una estación para ver su rendimiento de señal.")

# --- APP MAIN ---

def main():
    st.sidebar.title("📡 Meru Data Engine")
    uploaded_files = st.sidebar.file_uploader("Subir CSV de iDirect/Meru", type="csv", accept_multiple_files=True)
    
    if not uploaded_files:
        st.title("Sistema de Análisis de Reportes VNO")
        st.info("Por favor, sube los archivos CSV para generar el análisis automático.")
        return

    # Categorización de archivos
    for file in uploaded_files:
        with st.expander(f"📄 Procesando: {file.name}", expanded=False):
            try:
                df = clean_csv_header(file)
                cols = str(df.columns.tolist())
                
                if "Octets" in cols or "Usage" in file.name:
                    process_usage_report(df)
                elif "Eb/No" in cols or "Signal" in file.name:
                    process_ebno_report(df)
                else:
                    st.write("Archivo no identificado automáticamente. Vista previa:")
                    st.dataframe(df.head(5))
            except Exception as e:
                st.error(f"Error procesando el archivo: {e}")

if __name__ == "__main__":
    main()
