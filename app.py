import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random

# Configuración de página con estilo oscuro
st.set_page_config(
    page_title="Meru Networks | Global NOC",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS personalizado para emular una interfaz de monitoreo profesional
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    [data-testid="stMetricValue"] {
        color: #58a6ff;
        font-family: 'Courier New', Courier, monospace;
    }
    .status-header {
        color: #8b949e;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- GENERACIÓN DE DATOS SIMULADOS ---
def get_network_data():
    # Simulación de tráfico en Gbps (últimas 24 horas)
    df = pd.DataFrame({
        'Hora': pd.date_range(start='2024-05-20', periods=24, freq='H'),
        'Trafico_Gbps': [random.uniform(2, 8) for _ in range(24)],
        'Latencia_ms': [random.uniform(10, 25) for _ in range(24)]
    })
    return df

# --- HEADER DEL DASHBOARD ---
col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    st.markdown("# 🌐 MERU **NETWORKS**")
    st.markdown("<p class='status-header'>Global Network Operations Center • Live Stream</p>", unsafe_allow_stdio=True)

with col_h2:
    st.write("")
    now = datetime.now().strftime("%d %B %Y | %H:%M:%S")
    st.metric("SISTEMA UTC", now, delta="ESTABLE", delta_color="normal")

st.divider()

# --- KPIs PRINCIPALES ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Uptime Global", value="99.998%", delta="0.001%")
with kpi2:
    st.metric(label="Ancho de Banda Actual", value="5.4 Gbps", delta="-0.2 Gbps")
with kpi3:
    st.metric(label="Dispositivos Activos", value="1,248", delta="12")
with kpi4:
    st.metric(label="Alertas Críticas", value="0", delta="Normal", delta_color="inverse")

# --- GRÁFICOS INTERACTIVOS ---
df_data = get_network_data()

col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader("Rendimiento de Red (Throughput)")
    fig_line = px.line(df_data, x='Hora', y='Trafico_Gbps', 
                      template="plotly_dark",
                      color_discrete_sequence=['#58a6ff'])
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_chart2:
    st.subheader("Distribución de Carga")
    labels = ['WLAN-Internal', 'WLAN-Guest', 'VPN-Remote', 'DMZ']
    values = [450, 250, 150, 100]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
    fig_pie.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TABLA DE LOGS / INVENTARIO ---
st.subheader("Consola de Eventos en Tiempo Real")

eventos = [
    {"Hora": "14:05:22", "Dispositivo": "CORE-RT-01", "Evento": "BGP Session Re-established", "Status": "INFO"},
    {"Hora": "14:02:10", "Dispositivo": "DIST-SW-04", "Evento": "Port Te1/0/1 state changed to UP", "Status": "SUCCESS"},
    {"Hora": "13:58:45", "Dispositivo": "AP-OFFICE-09", "Evento": "Channel interference detected (5GHz)", "Status": "WARN"},
    {"Hora": "13:45:01", "Dispositivo": "EDGE-FW-01", "Evento": "DDoS Mitigation module active", "Status": "SECURITY"},
]

st.table(pd.DataFrame(eventos))

# Simulación de actualización (Opcional para local)
# st.empty()
# time.sleep(1)
# st.rerun()
