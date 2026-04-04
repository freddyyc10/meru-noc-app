import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Meru NOC Analytics",
    page_icon="📡",
    layout="wide"
)

# --- CORRECCIÓN DEL ERROR ---
# Se cambió unsafe_allow_stdio por unsafe_allow_html
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📡 Meru Networks - Dashboard NOC")
    st.subheader("Análisis de Rendimiento de Red")

    # Sidebar para carga de datos
    st.sidebar.header("Carga de Datos")
    uploaded_file = st.sidebar.file_uploader("Subir reporte CSV de Meru", type=["csv"])

    if uploaded_file is not None:
        try:
            # Leemos el CSV
            df = pd.read_csv(uploaded_file)
            
            # Limpieza básica de columnas (espacios en blanco)
            df.columns = [c.strip() for c in df.columns]

            # Layout de métricas principales
            col1, col2, col3 = st.columns(3)
            
            # Ejemplo de métricas (ajusta según los nombres de tus columnas reales)
            if 'Eb/No' in df.columns:
                avg_ebno = df['Eb/No'].mean()
                col1.metric("Eb/No Promedio", f"{avg_ebno:.2f} dB")
            
            if 'Traffic' in df.columns:
                total_traffic = df['Traffic'].sum()
                col2.metric("Tráfico Total", f"{total_traffic} MB")
                
            col3.metric("Estado del Sistema", "Online", delta="Estable")

            # Gráfico de serie temporal
            st.write("### Tendencia de Señal")
            # Buscamos columnas numéricas para graficar
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                selected_metric = st.selectbox("Seleccionar métrica para graficar", numeric_cols)
                fig = px.line(df, y=selected_metric, title=f"Histórico de {selected_metric}")
                st.plotly_chart(fig, use_container_width=True)

            # Tabla de datos
            with st.expander("Ver tabla de datos completa"):
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")
    else:
        st.info("Esperando carga de archivo CSV para mostrar estadísticas...")

if __name__ == "__main__":
    main()
