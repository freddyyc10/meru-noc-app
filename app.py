import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --- CONFIGURACION DE PAGINA ---
# Eliminamos acentos y caracteres especiales para evitar SyntaxError
st.set_page_config(
    page_title="NOC Meru Networks - Analizador",
    page_icon="📡",
    layout="wide"
)

# Estilos basicos para el dashboard
st.markdown("""
    <style>
    .stMetric {
        background-color: #161b22;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_stdio=True)

def get_clean_df(file):
    """Limpia el CSV saltando metadatos de iDirect hasta encontrar la cabecera"""
    try:
        # Leemos el archivo ignorando errores de decodificacion
        raw_content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
        skip_rows = 0
        
        # Palabras clave para detectar el inicio de los datos reales
        keywords = ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]
        
        for i, line in enumerate(raw_content):
            if any(key in line for key in keywords):
                skip_rows = i
                break
        
        file.seek(0)
        df = pd.read_csv(file, skiprows=skip_rows)
        # Limpiar nombres de columnas: quitar espacios y comillas
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error procesando el archivo: {str(e)}")
        return pd.DataFrame()

def show_signal_analysis(df):
    """Visualizacion de Eb/No y Niveles de Senal"""
    st.subheader("Analisis de Niveles de Senal (Eb/No)")
    
    ebno_cols = [c for c in df.columns if "Eb/No" in c]
    time_col = next((c for c in df.columns if "Time" in c or "Date" in c), None)

    if not ebno_cols:
        st.warning("No se detectaron columnas de Eb/No en este archivo.")
        return

    # Extraer nombres de estaciones
    stations = list(set([c.split('/')[0] for c in ebno_cols if '/' in c]))
    if not stations:
        stations = ebno_cols

    selected_station = st.selectbox("Seleccionar Estacion:", stations)
    
    # Filtrar columnas de la estacion seleccionada
    plot_data = [c for c in ebno_cols if selected_station in c]
    
    fig = go.Figure()
    for col in plot_data:
        fig.add_trace(go.Scatter(
            x=df[time_col] if time_col else df.index,
            y=df[col],
            name=col.split('/')[-1] if '/' in col else col,
            mode='lines'
        ))

    fig.update_layout(
        title=f"Historico de Senal: {selected_station}",
        hovermode="x unified",
        template="plotly_dark",
        xaxis=dict(title="Tiempo"),
        yaxis=dict(title="dB")
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Barra lateral
    st.sidebar.title("Meru NOC Dashboard")
    files = st.sidebar.file_uploader("Cargar Reportes CSV de iDirect", type="csv", accept_multiple_files=True)

    if not files:
        st.title("Sistema NOC Meru Networks")
        st.info("Por favor, suba los archivos CSV exportados desde iDirect para iniciar el analisis.")
        return

    # Resumen basico
    col1, col2 = st.columns(2)
    col1.metric("Archivos Cargados", len(files))
    col2.metric("Estado de Red", "Monitoreando")

    for f in files:
        with st.expander(f"Reporte: {f.name}", expanded=True):
            df = get_clean_df(f)
            if df.empty:
                st.warning(f"El archivo {f.name} no contiene datos validos.")
                continue
            
            # Busqueda de patrones en las columnas
            col_text = " ".join(df.columns).lower()
            
            if "eb/no" in col_text:
                show_signal_analysis(df)
            elif "octets" in col_text or "bit rate" in col_text:
                st.subheader("Analisis de Trafico")
                st.dataframe(df.head(10))
            else:
                st.write("Vista previa de datos desconocidos:")
                st.dataframe(df.head(10))

    # Pie de pagina limpio (sin simbolos especiales)
    st.markdown("---")
    st.caption("Meru Networks (c) 2024 - Sistema de Gestion de Red")

if __name__ == "__main__":
    main()
