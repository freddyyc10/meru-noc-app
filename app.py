import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Data Analysis",
    page_icon="📡",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; }
    h1, h2, h3 { color: #0f172a; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---

def get_clean_df(file):
    """Limpia el archivo CSV omitiendo metadatos iniciales de iDirect/Meru"""
    content = file.getvalue().decode('utf-8').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if "Date" in line or "/" in line or "Octets" in line:
            skip_rows = i
            break
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip_rows)
    df.columns = [c.strip() for c in df.columns]
    return df

def analyze_usage(df):
    """Procesa reportes de consumo de datos (Usage)"""
    st.subheader("📊 Análisis de Consumo de Datos")
    
    # Identificar estaciones (formato: Estacion / In Octets)
    stations = sorted(list(set([col.split(" / ")[0].strip() for col in df.columns if " / " in col])))
    
    if not stations:
        st.error("No se detectaron columnas de estaciones en el formato esperado (Estación / In/Out Octets).")
        st.write("Columnas detectadas:", df.columns.tolist())
        return

    report_data = []
    for site in stations:
        in_col = next((c for c in df.columns if site in c and "In" in c), None)
        out_col = next((c for c in df.columns if site in c and "Out" in c), None)
        
        if in_col and out_col:
            # Convertir de Octetos a MB
            down = pd.to_numeric(df[in_col], errors='coerce').sum() / (1024 * 1024)
            up = pd.to_numeric(df[out_col], errors='coerce').sum() / (1024 * 1024)
            
            if (down + up) > 0:
                report_data.append({
                    "Estación": site,
                    "Descarga (MB)": round(down, 2),
                    "Subida (MB)": round(up, 2),
                    "Total (MB)": round(down + up, 2)
                })

    if report_data:
        res_df = pd.DataFrame(report_data).sort_values("Total (MB)", ascending=False)
        
        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("Tráfico Total VNO", f"{res_df['Total (MB)'].sum():,.2f} MB")
        m2.metric("Top Consumo", res_df.iloc[0]['Estación'])
        m3.metric("Promedio x Estación", f"{res_df['Total (MB)'].mean():,.2f} MB")

        # Gráfico y Tabla
        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig = px.bar(res_df.head(15), x='Total (MB)', y='Estación', 
                         orientation='h', title="Top 15 Estaciones con mayor Consumo",
                         color='Total (MB)', color_continuous_scale='Viridis')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.write("### Detalle Completo")
            st.dataframe(res_df, hide_index=True, use_container_width=True)
            
            csv = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar CSV Procesado", csv, "reporte_limpio.csv", "text/csv")
    else:
        st.warning("El archivo parece estar vacío o no contiene valores numéricos válidos.")

def analyze_signal(df):
    """Procesa reportes de Eb/No (Signal)"""
    st.subheader("📶 Análisis de Niveles de Señal")
    
    date_col = next((c for c in df.columns if "Date" in c or "Time" in c), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Extraer estaciones
    stations = sorted(list(set([col.split(" / ")[0].strip() for col in df.columns if "/" in col])))
    
    selected_site = st.selectbox("Seleccione Estación para monitoreo temporal:", stations)
    
    # Buscar columnas FL/RL
    fl = next((c for c in df.columns if selected_site in c and ("FL" in c or "In" in c)), None)
    rl = next((c for c in df.columns if selected_site in c and ("RL" in c or "Out" in c)), None)

    if fl and rl:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[fl], name="Forward (FL) dB", line=dict(color='#2563eb')))
        fig.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[rl], name="Return (RL) dB", line=dict(color='#dc2626')))
        fig.update_layout(title=f"Estabilidad de Señal: {selected_site}", hovermode="x unified", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No se encontraron series temporales de señal para este sitio.")

# --- INTERFAZ PRINCIPAL ---

def main():
    st.sidebar.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=80)
    st.sidebar.title("Meru Engine v2.0")
    st.sidebar.markdown("---")
    
    uploaded_files = st.sidebar.file_uploader(
        "Cargar reportes de iDirect/Meru (.csv)", 
        type="csv", 
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.title("📡 Panel de Control NOC Meru")
        st.markdown("""
        ### Instrucciones:
        1. Sube tus archivos de **Data Usage** (Consumo) o **Eb/No** (Señal) en el panel izquierdo.
        2. El sistema detectará automáticamente el tipo de reporte.
        3. Podrás visualizar métricas, gráficos de tendencia y descargar el resumen.
        """)
        st.info("Esperando archivos CSV...")
        return

    for file in uploaded_files:
        with st.expander(f"📄 Archivo: {file.name}", expanded=True):
            try:
                df = get_clean_df(file)
                
                # Lógica de detección por contenido de columnas o nombre de archivo
                cols_str = " ".join(df.columns).lower()
                
                if "octets" in cols_str or "usage" in file.name.lower():
                    analyze_usage(df)
                elif "eb/no" in cols_str or "signal" in file.name.lower():
                    analyze_signal(df)
                else:
                    st.write("Vista previa del archivo (No categorizado):")
                    st.dataframe(df.head(10))
            except Exception as e:
                st.error(f"Error procesando el archivo: {str(e)}")

if __name__ == "__main__":
    main()
