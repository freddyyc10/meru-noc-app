import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Analizador",
    page_icon="📡",
    layout="wide"
)

def get_clean_df(file):
    """Limpia el CSV saltando metadatos de iDirect hasta encontrar la cabecera"""
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        # Buscamos palabras clave que definen el inicio de los datos
        if any(key in line for key in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
            skip_rows = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip_rows)
        # Limpiar nombres de columnas: quitar espacios y comillas
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

def analyze_usage(df):
    """Procesamiento de Consumo de Datos (In/Out)"""
    st.subheader("📊 Análisis de Consumo de Datos")
    
    all_cols = df.columns.tolist()
    # Identificar sitios buscando el patrón prefijo/sufijo
    sites = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
    
    if not sites:
        st.warning("No se detectaron columnas con formato de estación (ej: SITIO/Metrica)")
        return

    report = []
    for s in sites:
        # Buscamos columnas de entrada y salida para este sitio específico
        # Soportamos: ifInOctets, ifOutOctets, FL Bit Rate, RL Bit Rate
        in_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
        out_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
        
        if in_c or out_c:
            val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
            val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
            
            # Determinar unidad (Octetos -> MB, Bit Rate -> valor directo)
            is_bytes = "Octets" in str(in_c or out_c)
            factor = (1024 * 1024) if is_bytes else 1
            unit = "MB" if is_bytes else "Units"

            if (val_in + val_out) > 0:
                report.append({
                    "Estación": s,
                    f"In ({unit})": round(val_in / factor, 2),
                    f"Out ({unit})": round(val_out / factor, 2),
                    f"Total ({unit})": round((val_in + val_out) / factor, 2)
                })

    if report:
        res_df = pd.DataFrame(report).sort_values(by=f"Total ({unit})", ascending=False)
        
        m1, m2 = st.columns(2)
        m1.metric("Tráfico Total Acumulado", f"{res_df[f'Total ({unit})'].sum():,.2f} {unit}")
        m2.metric("Estación con más tráfico", res_df.iloc[0]['Estación'])

        fig = px.bar(res_df.head(15), x=f"Total ({unit})", y="Estación", orientation='h',
                     title="Top 15 Estaciones por Consumo", color=f"Total ({unit})")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(res_df, use_container_width=True, hide_index=True)

def analyze_signal(df):
    """Procesamiento de Niveles de Señal y Eb/No"""
    st.subheader("📶 Análisis de Niveles de Señal")
    
    all_cols = df.columns.tolist()
    # Buscar columna de tiempo
    time_col = next((c for c in all_cols if "Date" in c or "Time" in c), None)
    
    # Extraer estaciones
    stations = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
    
    if not stations:
        st.error("No se encontraron series de datos para graficar.")
        return

    selected = st.selectbox("Seleccione Estación para graficar:", stations, key="signal_select")
    
    if selected:
        # Filtrar columnas que pertenecen a la estación seleccionada
        plot_cols = [c for c in all_cols if c.startswith(selected + "/")]
        
        fig = go.Figure()
        x_axis = df[time_col] if time_col else df.index
        
        for c in plot_cols:
            fig.add_trace(go.Scatter(x=x_axis, y=df[c], name=c.split('/')[-1], mode='lines'))
            
        fig.update_layout(title=f"Histórico: {selected}", template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.sidebar.title("NOC Meru v2.0 📡")
    files = st.sidebar.file_uploader("Subir reportes CSV", type="csv", accept_multiple_files=True)

    if not files:
        st.title("Sistema de Monitoreo Meru Networks")
        st.info("Cargue los archivos CSV para generar el reporte visual.")
        return

    for f in files:
        with st.expander(f"Archivo: {f.name}", expanded=True):
            df = get_clean_df(f)
            if df.empty:
                continue
                
            cols_text = " ".join(df.columns).lower()
            # Si contiene Octets o Bit Rate, es reporte de consumo
            if any(k in cols_text for k in ["octets", "bit rate", "fl bit", "rl bit"]):
                analyze_usage(df)
            else:
                analyze_signal(df)

if __name__ == "__main__":
    main()
