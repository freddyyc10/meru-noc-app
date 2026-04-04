import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Data Analysis",
    page_icon="📡",
    layout="wide"
)

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

def get_clean_df(file):
    """Limpia el CSV buscando la fila de cabecera real"""
    content = file.getvalue().decode('utf-8').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        # Buscamos 'Date' o patrones comunes de iDirect
        if "Date" in line or "Octets" in line or "Eb/No" in line:
            skip_rows = i
            break
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip_rows)
    df.columns = [c.strip() for c in df.columns]
    return df

def analyze_usage(df):
    """Procesamiento robusto de Consumo de Datos"""
    st.subheader("📊 Análisis de Consumo de Datos")
    
    # Extraer nombres de estaciones únicos (todo lo que está antes del '/')
    all_cols = df.columns.tolist()
    potential_stations = []
    for col in all_cols:
        if "/" in col:
            station_name = col.split("/")[0].strip()
            if station_name not in ["Date", "Time"]:
                potential_stations.append(station_name)
    
    stations = sorted(list(set(potential_stations)))

    if not stations:
        st.error("No se detectaron estaciones. Formato de columnas no reconocido.")
        st.write("Columnas detectadas:", all_cols)
        return

    report_data = []
    for site in stations:
        # Buscamos columnas que contengan el nombre del sitio Y 'In' o 'Out'
        in_col = next((c for c in all_cols if site in c and ("InOctets" in c or "In Bit Rate" in c or "FL Bit" in c)), None)
        out_col = next((c for c in all_cols if site in c and ("OutOctets" in c or "Out Bit Rate" in c or "RL Bit" in c)), None)
        
        if in_col or out_col:
            # Sumar valores (ignorando NaNs)
            down_val = pd.to_numeric(df[in_col], errors='coerce').sum() if in_col else 0
            up_val = pd.to_numeric(df[out_col], errors='coerce').sum() if out_col else 0
            
            # Si es Octetos, convertir a MB. Si es Bit Rate, dejar como está (o ajustar según necesidad)
            # Asumimos Octetos por el nombre de tus columnas
            is_octets = "Octets" in (in_col or "") or "Octets" in (out_col or "")
            
            divisor = (1024 * 1024) if is_octets else 1 # Convertir a MB si son octetos
            unit = "MB" if is_octets else "Units"

            total = (down_val + up_val) / divisor
            
            if total > 0:
                report_data.append({
                    "Estación": site,
                    f"Descarga ({unit})": round(down_val / divisor, 2),
                    f"Subida ({unit})": round(up_val / divisor, 2),
                    f"Total ({unit})": round(total, 2)
                })

    if report_data:
        res_df = pd.DataFrame(report_data).sort_values(by=res_df.columns[-1], ascending=False)
        
        # Dashboard
        col_total = res_df.columns[-1]
        m1, m2, m3 = st.columns(3)
        m1.metric("Tráfico Total", f"{res_df[col_total].sum():,.2f} {unit}")
        m2.metric("Top Estación", res_df.iloc[0]['Estación'])
        m3.metric("Estaciones Activas", len(res_df))

        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig = px.bar(res_df.head(20), x=col_total, y='Estación', 
                         orientation='h', title="Top 20 Estaciones",
                         color=col_total, color_continuous_scale='Blues')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, template="simple_white")
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.write("### Tabla de Consumo")
            st.dataframe(res_df, hide_index=True, use_container_width=True)
    else:
        st.warning("No se pudieron extraer datos numéricos de las estaciones detectadas.")

def analyze_signal(df):
    """Procesamiento de Eb/No y Niveles"""
    st.subheader("📶 Análisis de Niveles de Señal")
    
    date_col = next((c for c in df.columns if "Date" in c or "Time" in c), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    # Identificar estaciones basadas en el prefijo antes del "/"
    stations = sorted(list(set([col.split("/")[0].strip() for col in df.columns if "/" in col])))
    
    selected_site = st.selectbox("Seleccione Estación:", stations)
    
    # Buscar cualquier columna que pertenezca a ese sitio
    site_cols = [c for c in df.columns if selected_site in c and c != date_col]
    
    if site_cols:
        fig = go.Figure()
        for col in site_cols:
            name = col.split("/")[-1] # Simplificar nombre para la leyenda
            fig.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[col], name=name))
        
        fig.update_layout(
            title=f"Monitoreo: {selected_site}",
            xaxis_title="Tiempo" if date_col else "Muestras",
            yaxis_title="Valor (dB / Rate)",
            hovermode="x unified",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No se encontraron datos para graficar en este sitio.")

def main():
    st.sidebar.title("Meru Engine 📡")
    uploaded_files = st.sidebar.file_uploader("Cargar reportes CSV", type="csv", accept_multiple_files=True)

    if not uploaded_files:
        st.title("Panel de Control NOC")
        st.info("Por favor, cargue los archivos CSV generados por iDirect para comenzar.")
        return

    for file in uploaded_files:
        with st.expander(f"Archivo: {file.name}", expanded=True):
            df = get_clean_df(file)
            cols_str = " ".join(df.columns).lower()
            
            # Decidir qué análisis aplicar
            if "octets" in cols_str or "bit rate" in cols_str:
                analyze_usage(df)
            else:
                analyze_signal(df)

if __name__ == "__main__":
    main()
