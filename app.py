import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru Networks | Global NOC",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DISEÑO DE INTERFAZ (CSS PERSONALIZADO) ---
# Se corrigió 'unsafe_allow_stdio' por 'unsafe_allow_html'
st.markdown("""
<style>
    /* Estilo General Dark Mode */
    .main {
        background-color: #0b0e14;
        color: #e6edf3;
    }
    
    /* Tarjetas de Métricas Estilizadas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #58a6ff !important;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid #30363d;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
    }

    /* Contenedores de Gráficos */
    .chart-container {
        background: #161b22;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }

    /* Títulos y Subtítulos */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #238636;
        margin-right: 8px;
        box-shadow: 0 0 10px #238636;
    }

    /* Personalización de barra lateral y otros elementos */
    .stAppHeader { background: rgba(0,0,0,0); }
    
</style>
""", unsafe_allow_html=True)

# --- GENERACIÓN DE DATOS (MOCK DATA) ---
def load_data():
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Tráfico Int', 'Tráfico Ext', 'Latencia']
    )
    return chart_data

data = load_data()

# --- HEADER PRINCIPAL ---
col_logo, col_info = st.columns([3, 1])

with col_logo:
    st.markdown("""
        <div style="display: flex; align-items: center;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #ffffff;">MERU <span style="color: #58a6ff;">NETWORKS</span></h1>
            <div style="margin-left: 20px; padding: 5px 15px; background: rgba(35, 134, 54, 0.2); border: 1px solid #238636; border-radius: 20px;">
                <span class="status-indicator"></span><span style="color: #3fb950; font-weight: 500; font-size: 0.9rem;">SISTEMAS OPERATIVOS</span>
            </div>
        </div>
        <p style="color: #8b949e; margin-top: 10px;">Global Network Operations Center | Real-Time Monitoring</p>
    """, unsafe_allow_html=True)

with col_info:
    st.markdown(f"""
        <div style="text-align: right; color: #8b949e; font-family: monospace;">
            ID SESIÓN: {hex(int(time.time())).upper()}<br>
            TIMESTAMP: {datetime.now().strftime('%H:%M:%S')}<br>
            REGIÓN: LATAM-HQ
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- FILA 1: KPIs ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("UPTIME ANUAL", "99.998%", "0.001%")
with kpi2:
    st.metric("ANCHO DE BANDA", "4.2 Tbps", "+12%", delta_color="normal")
with kpi3:
    st.metric("LATENCIA MEDIA", "14.2 ms", "-2.1 ms", delta_color="inverse")
with kpi4:
    st.metric("AMENAZAS BLOCK", "1,242", "Normal")

st.markdown("<br>", unsafe_allow_html=True)

# --- FILA 2: GRÁFICOS PRINCIPALES ---
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### Rendimiento de Carga (Global)")
    fig = px.area(data, template="plotly_dark", color_discrete_sequence=['#58a6ff', '#1f6feb', '#238636'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#30363d')
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### Estado de Nodos")
    labels = ['Activos', 'Mantenimiento', 'Críticos']
    values = [85, 12, 3]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
    fig_pie.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig_pie.update_traces(marker=dict(colors=['#238636', '#d29922', '#f85149']))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- FILA 3: TABLA DE EVENTOS ---
st.markdown("### Log de Eventos en Tiempo Real")
event_data = pd.DataFrame([
    {"ID": "ERR-90", "Timestamp": "14:02:11", "Nodo": "AR-BUE-01", "Evento": "BGP Flapping", "Prioridad": "ALTA"},
    {"ID": "INF-22", "Timestamp": "14:01:45", "Nodo": "BR-SAO-02", "Evento": "Backup Sync Complete", "Prioridad": "BAJA"},
    {"ID": "WRN-04", "Timestamp": "13:59:02", "Nodo": "CL-SAN-01", "Evento": "Temp Threshold Exceeded", "Prioridad": "MEDIA"},
    {"ID": "INF-21", "Timestamp": "13:55:20", "Nodo": "MX-CDX-04", "Evento": "User Auth Success", "Prioridad": "BAJA"}
])

def color_priority(val):
    if val == 'ALTA': return 'color: #f85149'
    if val == 'MEDIA': return 'color: #d29922'
    return 'color: #3fb950'

st.dataframe(
  event_data.style.map(color_priority, subset=['Prioridad']),
    use_container_width=True,
    hide_index=True
)

# --- FOOTER ---
st.markdown("""
    <div style="text-align: center; color: #8b949e; padding: 40px 0;">
        <small>© 2024 Meru Networks. Todos los derechos reservados. Confidencial.</small>
    </div>
""", unsafe_allow_html=True)
