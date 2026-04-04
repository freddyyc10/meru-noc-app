import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        background-color: white;
    }
    .status-online { color: #10b981; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def get_csv_download_link(df, filename):
    """Genera un link de descarga para los datos procesados"""
    csv = df.to_csv(index=False)
    return st.download_button(
        label=f"📥 Descargar {filename}",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )

def identify_date_col(df):
    """Identifica la columna de fecha sin importar el nombre exacto"""
    for col in ["Date (UTC)", "Date", "Timestamp", "time"]:
        if col in df.columns:
            return col
    return None

# --- PROCESAMIENTO DE MÓDULOS ---

def process_ebno(df, stations):
    st.header("📊 Análisis de Señal Satelital (Eb/No)")
    
    date_col = identify_date_col(df)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_st = st.selectbox("Seleccionar Estación", sorted(list(stations)), key="ebno_select")
        
        # Filtro de fecha simple
        if date_col:
            min_date = df[date_col].min().date()
            max_date = df[date_col].max().date()
            date_range = st.date_input("Rango de fechas", [min_date, max_date])
            
            if len(date_range) == 2:
                df = df[(df[date_col].dt.date >= date_range[0]) & (df[date_col].dt.date <= date_range[1])]

    fl_col = f"{selected_st}/FL Tuner Eb/No"
    rl_col = f"{selected_st}/RL Measured Eb/No"
    
    if fl_col in df.columns and rl_col in df.columns:
        # Gráfica interactiva
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col], y=df[fl_col], name="Forward Link", line=dict(color='#3b82f6', width=2)))
        fig.add_trace(go.Scatter(x=df[date_col], y=df[rl_col], name="Return Link", line=dict(color='#f59e0b', width=2)))
        
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Tiempo (UTC)",
            yaxis_title="Eb/No (dB)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0),
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas Rápidas
        c1, c2, c3 = st.columns(3)
        c1.metric("Promedio FL", f"{df[fl_col].mean():.2f} dB")
        c2.metric("Promedio RL", f"{df[rl_col].mean():.2f} dB")
        # Estimación de disponibilidad (ejemplo: Eb/No > 4)
        uptime = (df[fl_col] > 4).sum() / len(df) * 100
        c3.metric("Est. Disponibilidad", f"{uptime:.1f}%")
    else:
        st.error(f"⚠️ Las columnas de Eb/No para '{selected_st}' no se encuentran en este archivo.")

def process_usage(df, stations):
    st.header("💾 Reporte de Consumo de Datos")
    
    usage_list = []
    for st_name in stations:
        in_col = f"{st_name} In"
        out_col = f"{st_name} Out"
        if in_col in df.columns and out_col in df.columns:
            total_in = df[in_col].sum()
            total_out = df[out_col].sum()
            usage_list.append({
                "Estación": st_name,
                "Descarga (MB)": round(total_in, 2),
                "Subida (MB)": round(total_out, 2),
                "Total (MB)": round(total_in + total_out, 2)
            })
    
    if usage_list:
        usage_df = pd.DataFrame(usage_list).sort_values("Total (MB)", ascending=False)
        
        col_chart, col_data = st.columns([2, 1])
        with col_chart:
            fig = px.pie(usage_df.head(8), values='Total (MB)', names='Estación', 
                         title="Distribución de Tráfico (Top 8 Estaciones)",
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
            fig_bar = px.bar(usage_df.head(15), x="Estación", y=["Descarga (MB)", "Subida (MB)"],
                             title="Comparativa Descarga vs Subida", barmode="group")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_data:
            st.write("### Resumen")
            st.dataframe(usage_df, hide_index=True, use_container_width=True)
            get_csv_download_link(usage_df, "consumo_total.csv")
    else:
        st.info("Sube un archivo de 'Data Usage' para activar este módulo.")

# --- APP PRINCIPAL ---
def main():
    # Barra Lateral
    with st.sidebar:
        st.title("📡 Meru NOC")
        st.markdown("*Herramienta de Diagnóstico Operativo*")
        st.divider()
        
        uploaded_files = st.file_uploader(
            "Subir Reportes CSV", 
            type=["csv"], 
            accept_multiple_files=True,
            help="Puedes subir múltiples archivos de Eb/No, Octetos o Uso de Datos simultáneamente."
        )
        
        if uploaded_files:
            st.success(f"{len(uploaded_files)} archivos cargados.")
            if st.button("Limpiar Cache"):
                st.rerun()
        
        st.divider()
        st.markdown("🔒 **Seguridad**: Los datos se procesan localmente en la sesión y no se guardan permanentemente.")

    if not uploaded_files:
        st.title("Bienvenido al Portal de Monitoreo")
        st.subheader("Para comenzar, carga tus archivos en el panel izquierdo.")
        
        # Dashboard de bienvenida visual
        cols = st.columns(3)
        with cols[0]:
            st.info("📶 **Monitoreo Satelital**\nVisualiza niveles Eb/No y estabilidad de señal.")
        with cols[1]:
            st.info("📉 **Tráfico de Red**\nAnaliza el flujo de octetos y congestión.")
        with cols[2]:
            st.info("💰 **Reporte de Uso**\nGenera resúmenes de consumo por estación.")
        
        st.image("https://images.unsplash.com/photo-1551703599-6b3e8379aa8b?q=80&w=1000&auto=format&fit=crop", caption="NOC Infrastructure", use_container_width=True)
        return

    # Estructura de datos consolidada
    data_dict = {"ebno": None, "usage": None, "octets": None}
    all_stations = set()

    for file in uploaded_files:
        try:
            df = pd.read_csv(file)
            cols = df.columns.tolist()
            
            # Lógica de detección de tipo de archivo
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
        except Exception as e:
            st.error(f"Error procesando {file.name}: {e}")

    # HEADER PRINCIPAL CON MÉTRICAS
    st.title("🚀 Dashboard de Operaciones")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Estaciones Únicas", len(all_stations))
    m2.metric("Archivos Activos", sum(1 for v in data_dict.values() if v is not None))
    m3.metric("Último Reporte", datetime.now().strftime("%H:%M:%S"))
    m4.metric("Status", "EN LÍNEA", delta_color="normal")

    # SISTEMA DE PESTAÑAS
    tabs = []
    if data_dict["ebno"] is not None: tabs.append("📶 Niveles Eb/No")
    if data_dict["usage"] is not None: tabs.append("💾 Consumo Data")
    if data_dict["octets"] is not None: tabs.append("📈 Tráfico Red")

    if tabs:
        st_tabs = st.tabs(tabs)
        
        for i, tab_name in enumerate(tabs):
            with st_tabs[i]:
                if "Eb/No" in tab_name:
                    process_ebno(data_dict["ebno"], all_stations)
                elif "Consumo" in tab_name:
                    process_usage(data_dict["usage"], all_stations)
                elif "Tráfico" in tab_name:
                    st.header("📈 Monitoreo de Tráfico de Octetos")
                    search_st = st.selectbox("Seleccionar Estación para Tráfico", sorted(list(all_stations)))
                    
                    df_oct = data_dict["octets"]
                    date_c = identify_date_col(df_oct)
                    if date_c: df_oct[date_c] = pd.to_datetime(df_oct[date_c])
                    
                    # Graficar In vs Out si existen
                    in_oct = [c for c in df_oct.columns if search_st in c and "ifInOctets" in c]
                    out_oct = [c for c in df_oct.columns if search_st in c and "ifOutOctets" in c]
                    
                    if in_oct and out_oct:
                        fig_oct = go.Figure()
                        fig_oct.add_trace(go.Scatter(x=df_oct[date_c], y=df_oct[in_oct[0]], name="Entrada (In)", fill='tozeroy'))
                        fig_oct.add_trace(go.Scatter(x=df_oct[date_c], y=df_oct[out_oct[0]], name="Salida (Out)", fill='tozeroy'))
                        fig_oct.update_layout(title=f"Tráfico Octetos - {search_st}", hovermode="x unified")
                        st.plotly_chart(fig_oct, use_container_width=True)
                    else:
                        st.warning("No se encontraron columnas de octetos para esta estación.")
    else:
        st.warning("Los archivos subidos no coinciden con los formatos conocidos de Meru Networks.")

if __name__ == "__main__":
    main()
