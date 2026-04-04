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
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CARGA INTELIGENTE ---

def smart_load_csv(file):
    """
    Detecta automáticamente dónde empiezan los datos reales en el CSV 
    saltando los encabezados de metadatos de los reportes iDirect.
    """
    # Leer las primeras 20 líneas para encontrar el encabezado real
    content = file.getvalue().decode('utf-8').splitlines()
    skip_rows = 0
    
    for i, line in enumerate(content):
        # Buscamos palabras clave comunes en la fila de títulos
        if "Date" in line or "Timestamp" in line or "Eb/No" in line or "Octets" in line:
            skip_rows = i
            break
            
    file.seek(0) # Resetear puntero del archivo
    return pd.read_csv(file, skiprows=skip_rows)

def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    return st.download_button(
        label=f"📥 Descargar {filename}",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )

def identify_date_col(df):
    for col in ["Date (UTC)", "Date", "Timestamp", "time"]:
        if col in df.columns:
            return col
    return None

# --- PROCESAMIENTO DE MÓDULOS ---

def process_ebno(df, stations):
    st.header("📊 Análisis de Señal Satelital (Eb/No)")
    date_col = identify_date_col(df)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
    
    selected_st = st.selectbox("Seleccionar Estación", sorted(list(stations)), key="ebno_select")

    fl_col = next((c for c in df.columns if selected_st in c and "FL" in c), None)
    rl_col = next((c for c in df.columns if selected_st in c and "RL" in c), None)
    
    if fl_col and rl_col:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df[date_col], y=df[fl_col], name="Forward Link", line=dict(color='#3b82f6')))
        fig.add_trace(go.Scatter(x=df[date_col], y=df[rl_col], name="Return Link", line=dict(color='#f59e0b')))
        fig.update_layout(hovermode="x unified", height=450, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Promedio FL", f"{df[fl_col].mean():.2f} dB")
        c2.metric("Promedio RL", f"{df[rl_col].mean():.2f} dB")
        uptime = (df[fl_col] > 4).sum() / len(df) * 100
        c3.metric("Est. Disponibilidad", f"{uptime:.1f}%")
    else:
        st.error(f"⚠️ No se encontraron datos para '{selected_st}'")

def process_usage(df, stations):
    st.header("💾 Reporte de Consumo de Datos")
    
    usage_list = []
    for st_name in stations:
        # Buscamos columnas que contengan el nombre de la estación y 'In' o 'Out'
        in_col = next((c for c in df.columns if st_name in c and "In" in c), None)
        out_col = next((c for c in df.columns if st_name in c and "Out" in c), None)
        
        if in_col and out_col:
            total_in = pd.to_numeric(df[in_col], errors='coerce').sum()
            total_out = pd.to_numeric(df[out_col], errors='coerce').sum()
            if total_in + total_out > 0:
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
            fig = px.pie(usage_df.head(10), values='Total (MB)', names='Estación', hole=0.4, title="Top 10 Estaciones por Consumo")
            st.plotly_chart(fig, use_container_width=True)
        with col_data:
            st.dataframe(usage_df, hide_index=True)
            get_csv_download_link(usage_df, "consumo_total.csv")
    else:
        st.warning("No se detectó tráfico en las estaciones para este archivo.")

# --- APP PRINCIPAL ---
def main():
    with st.sidebar:
        st.title("📡 Meru NOC")
        uploaded_files = st.file_uploader("Subir Reportes CSV", type=["csv"], accept_multiple_files=True)
        if st.button("Reiniciar App"): st.rerun()

    if not uploaded_files:
        st.title("Panel de Control NOC")
        st.info("Cargue los archivos CSV (Eb/No, Data Usage u Octetos) para comenzar.")
        return

    data_dict = {"ebno": None, "usage": None, "octets": None}
    all_stations = set()

    for file in uploaded_files:
        try:
            # Usamos la carga inteligente para saltar metadatos
            df = smart_load_csv(file)
            cols = df.columns.tolist()
            
            # Clasificación por contenido de columnas
            if any("Eb/No" in c for c in cols):
                data_dict["ebno"] = df
                for c in cols: 
                    if "/" in c: all_stations.add(c.split("/")[0])
            
            elif any(" In" in c for c in cols) or "In Octets" in str(cols):
                data_dict["usage"] = df
                for c in cols:
                    if " In" in c: all_stations.add(c.replace(" In", ""))
                    elif "/" in c: all_stations.add(c.split("/")[0])
            
            elif any("Octets" in c for c in cols):
                data_dict["octets"] = df
                for c in cols:
                    if "/" in c: all_stations.add(c.split("/")[0])
                    
        except Exception as e:
            st.error(f"Error en {file.name}: {e}")

    # HEADER
    st.title("🚀 Monitoreo Operativo")
    m1, m2, m3 = st.columns(3)
    m1.metric("Estaciones", len(all_stations))
    m2.metric("Archivos", len(uploaded_files))
    m3.metric("Última Actualización", datetime.now().strftime("%H:%M"))

    tabs = []
    if data_dict["ebno"] is not None: tabs.append("📶 Eb/No")
    if data_dict["usage"] is not None: tabs.append("💾 Uso de Datos")
    if data_dict["octets"] is not None: tabs.append("📈 Octetos")

    if tabs:
        st_tabs = st.tabs(tabs)
        for i, tab_name in enumerate(tabs):
            with st_tabs[i]:
                if "Eb/No" in tab_name: process_ebno(data_dict["ebno"], all_stations)
                if "Uso" in tab_name: process_usage(data_dict["usage"], all_stations)
                if "Octetos" in tab_name:
                    st.write("Visualización de tráfico bruto por interfaz.")
                    st.dataframe(data_dict["octets"].head(10))

if __name__ == "__main__":
    main()
          
