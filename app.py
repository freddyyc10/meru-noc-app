import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# 1. Configuración de página (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title="Meru Networks | Global NOC",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inyección de CSS corregida
# Nota: Se usa unsafe_allow_html=True (stdio era un error de sintaxis)
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #161b22 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #30363d !important;
    }
    .status-header {
        color: #8b949e;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Funciones de Datos
def get_network_data():
    df = pd.DataFrame({
        'Hora': pd.date_range(start=datetime.now().strftime("%Y-%m-%d"), periods=24, freq='h'),
        'Trafico_Gbps': [random.uniform(2, 8) for _ in range(24)],
        'Latencia_ms': [random.uniform(10, 25) for _ in range(24)]
    })
    return df

# 4. Layout Superior
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    st.markdown("# 🌐 MERU **NETWORKS**")
    st.markdown("<p class='status-header'>Global Network Operations Center • Live Stream</p>", unsafe_allow_html=True)

with col_h2:
    now_str = datetime.now().strftime("%d %B %Y | %H:%M:%S")
    st.metric("SISTEMA UTC", now_str, delta="ESTABLE")

st.divider()

# 5. KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Uptime Global", "99.99%", "0.01%")
k2.metric("Tráfico Actual", "5.4 Gbps", "-0.2")
k3.metric("Nodos Activos", "1,248", "12")
k4.metric("Alertas", "0", "Normal")

# 6. Gráficos
df_data = get_network_data()
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Rendimiento de Red")
    fig_line = px.line(df_data, x='Hora', y='Trafico_Gbps', template="plotly_dark")
    fig_line.update_traces(line_color='#58a6ff')
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Segmentación")
    fig_pie = go.Figure(data=[go.Pie(labels=['Int', 'Ext', 'VPN'], values=[450, 250, 150], hole=.5)])
    fig_pie.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# 7. Tabla de Logs
st.subheader("Eventos de Red")
logs = pd.DataFrame([
    {"Time": "14:05", "Device": "CORE-01", "Msg": "BGP Up", "Type": "INFO"},
    {"Time": "14:02", "Device": "SW-04", "Msg": "Port Up", "Type": "SUCCESS"},
    {"Time": "13:58", "Device": "AP-09", "Msg": "Interference", "Type": "WARN"}
])
st.dataframe(logs, use_container_width=True)
