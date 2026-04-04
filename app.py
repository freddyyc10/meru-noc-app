import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="NOC Meru Networks - Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para mejorar la interfaz
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def process_ebno(df, stations):
    """Procesa y visualiza datos de Eb/No"""
    st.subheader("📊 Análisis de Señal Satelital (Eb/No)")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_st = st.selectbox("Seleccionar Estación", sorted(list(stations)), key="ebno_select")
        
    # Columnas esperadas
    fl_col = f"{selected_st}/FL Tuner Eb/No"
    rl_col = f"{selected_st}/RL Measured Eb/No"
    date_col = "Date (UTC)" if "Date (UTC)" in df.columns else "Date"
    
    if fl_col in df.columns and rl_col in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col], y=df[fl_col], name="Forward Link", line=dict(color='#3b82f6')))
        fig.add_trace(go.Scatter(x=df[date_col], y=df[rl_col], name="Return Link", line=dict(color='#f59e0b')))
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No se encontraron columnas de Eb/No para {selected_st}")

def process_usage(df, stations):
    """Procesa y visualiza reporte de uso de datos"""
    st.subheader("💾 Consumo de Datos (MB)")
    
    usage_data = []
    for st_name in stations:
        in_col = f"{st_name} In"
        out_col = f"{st_name} Out"
        if in_col in df.columns and out_col in df.columns:
            total_in = df[in_col].sum()
            total_out = df[out_col].sum()
            usage_data.append({
                "Estación": st_name,
                "Descarga (MB)": round(total_in, 2),
                "Subida (MB)": round(total_out, 2),
                "Total (MB)": round(total_in + total_out, 2)
            })
    
    if usage_data:
        usage_df = pd.DataFrame(usage_data).sort_values("Total (MB)", ascending=False)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(usage_df.head(10), x="Estación", y=["Descarga (MB)", "Subida (MB)"], 
                         title="Top 10 Estaciones por Consumo", barmode="stack",
                         color_discrete_sequence=['#3b82f6', '#94a3b8'])
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.dataframe(usage_df, hide_index=True, use_container_width=True)
    else:
        st.info("Sube un archivo de 'Data Usage Report' para ver estas métricas.")

def main():
    # Sidebar: Logo y Carga de Archivos
    with st.sidebar:
        st.title("📡 Meru NOC")
        st.markdown("---")
        uploaded_files = st.file_uploader("Cargar archivos CSV", type="csv", accept_multiple_files=True)
        st.info("Tipos: Statistics (Eb/No), Octets o Data Usage.")

    if not uploaded_files:
        st.title("Bienvenido al Dashboard del NOC")
        st.image("https://img.freepik.com/free-vector/network-monitoring-concept-illustration_114360-5023.jpg", width=400)
        st.markdown("""
        ### Instrucciones:
        1. Localiza tus reportes CSV de **Meru Networks**.
        2. Arrástralos al panel lateral izquierdo.
        3. El sistema detectará automáticamente si son datos de señal, tráfico o consumo.
        """)
        return

    # Consolidación de datos
    all_stations = set()
    data_dict = {"ebno": None, "usage": None, "octets": None}

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        cols = df.columns.tolist()
        
        # Identificar tipo de archivo por sus columnas
        if any("Eb/No" in c for c in cols):
            data_dict["ebno"] = df
            for c in cols:
                if "/" in c: all_stations.add(c.split("/")[0])
        
        elif any(" In" in c for c in cols) and any(" Out" in c for c in cols):
            data_dict["usage"] = df
            for c in cols:
                if " In" in c: all_stations.add(c.replace(" In", ""))
        
        elif any("Octets" in c for c in cols):
            data_dict["octets"] = df
            for c in cols:
                if "/" in c: all_stations.add(c.split("/")[0])

    # Header Principal
    st.title("🚀 Panel de Control Operativo")
    
    # KPIs Rápidos
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Estaciones", len(all_stations))
    
    total_recs = sum(len(d) for d in data_dict.values() if d is not None)
    kpi2.metric("Registros Totales", f"{total_recs:,}")
    
    modulos = sum(1 for d in data_dict.values() if d is not None)
    kpi3.metric("Módulos Activos", modulos)
    
    kpi4.metric("Estado NOC", "ONLINE", delta="Estable")

    # Pestañas de Navegación
    tab_list = []
    if data_dict["ebno"] is not None: tab_list.append("📡 Niveles Eb/No")
    if data_dict["usage"] is not None: tab_list.append("💾 Consumo Data")
    if data_dict["octets"] is not None: tab_list.append("📈 Tráfico Octetos")

    if tab_list:
        tabs = st.tabs(tab_list)
        
        for i, tab_name in enumerate(tab_list):
            with tabs[i]:
                if "Eb/No" in tab_name:
                    process_ebno(data_dict["ebno"], all_stations)
                elif "Consumo" in tab_name:
                    process_usage(data_dict["usage"], all_stations)
                elif "Octetos" in tab_name:
                    st.subheader("📈 Monitoreo de Tráfico (Octetos)")
                    search = st.text_input("Buscar estación...", key="search_oct").upper()
                    
                    df_oct = data_dict["octets"]
                    date_col = "Date (UTC)" if "Date (UTC)" in df_oct.columns else "Date"
                    target_cols = [c for c in df_oct.columns if search in c and "ifInOctets" in c][:5]
                    
                    if target_cols:
                        fig_oct = px.line(df_oct, x=date_col, y=target_cols, title="Tráfico de Entrada")
                        st.plotly_chart(fig_oct, use_container_width=True)
                    else:
                        st.info("Ingresa el nombre de una estación para ver su tráfico.")

if __name__ == "__main__":
    main()
