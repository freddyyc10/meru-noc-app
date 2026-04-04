import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Meru NOC - Network Operations Center",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS ---
# CORRECCIÓN: Se utiliza unsafe_allow_html=True
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    div[data-testid="stMetricValue"] {
        color: #58a6ff;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data(file):
    df = pd.read_csv(file)
    # Limpiar nombres de columnas y convertir fechas si existen
    df.columns = [c.strip() for c in df.columns]
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

def main():
    st.title("📡 Meru NOC Dashboard")
    st.markdown("### Centro de Operaciones de Red - Monitoreo en Tiempo Real")

    # Sidebar
    st.sidebar.image("https://via.placeholder.com/150x50?text=MERU+NETWORKS", use_container_width=True)
    st.sidebar.title("Controles de Red")
    uploaded_file = st.sidebar.file_uploader("Cargar Telemetría (CSV)", type=["csv"])
    
    refresh_rate = st.sidebar.slider("Frecuencia de actualización (seg)", 5, 60, 30)

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # --- MÉTRICAS DE ALTO NIVEL ---
        col1, col2, col3, col4 = st.columns(4)
        
        # Lógica de negocio (Eb/No, Tráfico, Latencia)
        if 'Eb/No' in df.columns:
            val = df['Eb/No'].iloc[-1]
            col1.metric("Eb/No Actual", f"{val:.2f} dB", delta=f"{val - df['Eb/No'].mean():.2f}")
        
        if 'Latency' in df.columns:
            lat = df['Latency'].iloc[-1]
            col2.metric("Latencia MS", f"{int(lat)} ms", delta="-2ms", delta_color="inverse")

        if 'PacketLoss' in df.columns:
            pl = df['PacketLoss'].iloc[-1]
            col3.metric("Pérdida de Paquetes", f"{pl}%", delta="0.5%", delta_color="inverse")
            
        col4.metric("Nodos Activos", "142", delta="3")

        # --- SECCIÓN DE ANÁLISIS VISUAL ---
        st.write("---")
        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("Rendimiento del Enlace (Eb/No)")
            if 'Eb/No' in df.columns and 'Timestamp' in df.columns:
                fig_signal = px.line(df, x='Timestamp', y='Eb/No', 
                                   title="Estabilidad de la Señal Satelital",
                                   template="plotly_dark")
                fig_signal.update_traces(line_color='#58a6ff')
                st.plotly_chart(fig_signal, use_container_width=True)
            else:
                st.warning("El CSV debe contener 'Timestamp' y 'Eb/No' para graficar la señal.")

        with c2:
            st.subheader("Distribución de Carga")
            if 'TrafficType' in df.columns:
                fig_pie = px.pie(df, names='TrafficType', title="Tipos de Tráfico Detectados",
                               hole=0.4, template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Agregue columna 'TrafficType' para ver distribución.")

        # --- MAPA DE CALOR O ESTADO DE NODOS ---
        st.subheader("Estado de Nodos en Red")
        if 'NodeID' in df.columns and 'Status' in df.columns:
            # Simulamos una vista de cuadrícula de nodos
            nodes = df[['NodeID', 'Status']].drop_duplicates().tail(20)
            cols = st.columns(5)
            for i, (_, row) in enumerate(nodes.iterrows()):
                color = "#238636" if row['Status'] == 'Active' else "#da3633"
                cols[i % 5].markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center; color: white; margin-bottom: 10px;">
                        {row['NodeID']}<br><b>{row['Status']}</b>
                    </div>
                """, unsafe_allow_html=True)

        # --- REGISTRO DE EVENTOS (LOGS) ---
        st.write("---")
        with st.expander("Ver Logs de Sistema y Raw Data"):
            st.dataframe(df.sort_values(by='Timestamp' if 'Timestamp' in df.columns else df.columns[0], ascending=False))

    else:
        # Estado inicial si no hay archivo
        st.info("Inicie la sesión cargando el archivo de telemetría de los equipos Meru.")
        
        # Placeholder visual
        st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1000", 
                 caption="Monitoreo Global Meru Networks", use_container_width=True)

if __name__ == "__main__":
    main()
