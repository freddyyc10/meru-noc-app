import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# Configuración de la página
st.set_page_config(page_title="Analizador Meru VNO", layout="wide")

st.title("📊 Analizador de Red Meru VNO")
st.markdown("Herramienta de procesamiento para reportes de tráfico y calidad de señal.")

def process_data(usage_file, stats_file):
    try:
        # 1. Cargar Reporte de Uso (Saltando 3 líneas de encabezado)
        # Basado en 'VNO Meru-Networks Data Usage Report (20).csv'
        df_usage_raw = pd.read_csv(usage_file, skiprows=3)
        
        # 2. Cargar Estadísticas (Eb/No)
        # Basado en 'statistics (44).csv'
        df_stats_raw = pd.read_csv(stats_file)

        # --- PROCESAMIENTO DE TRÁFICO ---
        cols_traffic = [c for c in df_usage_raw.columns if c != 'Date']
        # Obtener nombres de estaciones únicos quitando " In" y " Out"
        stations = sorted(list(set([c.rsplit(' ', 1)[0] for c in cols_traffic])))
        
        usage_data = []
        for s in stations:
            col_in = f"{s} In"
            col_out = f"{s} Out"
            
            val_in = pd.to_numeric(df_usage_raw[col_in], errors='coerce').sum() if col_in in df_usage_raw.columns else 0
            val_out = pd.to_numeric(df_usage_raw[col_out], errors='coerce').sum() if col_out in df_usage_raw.columns else 0
            
            usage_data.append({
                "Estación": s,
                "Descarga (MB)": round(val_in, 2),
                "Carga (MB)": round(val_out, 2),
                "Total (MB)": round(val_in + val_out, 2)
            })
            
        df_usage = pd.DataFrame(usage_data).sort_values(by="Total (MB)", ascending=False)

        # --- PROCESAMIENTO DE EB/NO ---
        ebno_data = []
        ebno_cols = [c for c in df_stats_raw.columns if 'Eb/No' in c]
        
        for col in ebno_cols:
            # El formato suele ser "NOMBRE_ESTACION/Tipo Eb/No"
            parts = col.split('/')
            station_name = parts[0].strip()
            tipo = "Forward Link" if "FL" in col else "Return Link"
            
            avg_val = pd.to_numeric(df_stats_raw[col], errors='coerce').mean()
            
            if not np.isnan(avg_val):
                ebno_data.append({
                    "Estación": station_name,
                    "Tipo": tipo,
                    "Eb/No Promedio (dB)": round(avg_val, 2)
                })
        
        df_ebno = pd.DataFrame(ebno_data)
        
        return df_usage, df_ebno

    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
        return None, None

# --- Zona de Carga de Archivos ---
col1, col2 = st.columns(2)
with col1:
    u_file = st.file_uploader("Subir Reporte de Uso (Usage Report)", type="csv")
with col2:
    s_file = st.file_uploader("Subir Estadísticas (Statistics)", type="csv")

if u_file and s_file:
    df_u, df_e = process_data(u_file, s_file)
    
    if df_u is not None:
        # Métricas de Resumen
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        total_red = df_u['Total (MB)'].sum()
        m1.metric("Tráfico Total", f"{total_red/1024:.2f} GB")
        m2.metric("Estaciones Activas", len(df_u))
        
        if not df_e.empty:
            avg_fl = df_e[df_e['Tipo'] == 'Forward Link']['Eb/No Promedio (dB)'].mean()
            m3.metric("Promedio Eb/No FL", f"{avg_fl:.2f} dB")
            
            low_signal = len(df_e[df_e['Eb/No Promedio (dB)'] < 8.0])
            m4.metric("Estaciones Alerta (<8dB)", low_signal)

        # Pestañas de Visualización
        tab_t, tab_s = st.tabs(["📊 Tráfico de Datos", "📡 Calidad de Señal"])
        
        with tab_t:
            st.subheader("Consumo por Estación")
            fig_usage = px.bar(df_u.head(20), x='Estación', y=['Descarga (MB)', 'Carga (MB)'],
                               title="Top 20 Estaciones por Consumo",
                               barmode='group',
                               color_discrete_map={'Descarga (MB)': '#00CC96', 'Carga (MB)': '#636EFA'})
            st.plotly_chart(fig_usage, use_container_width=True)
            
            st.dataframe(df_u, use_container_width=True, hide_index=True)

        with tab_s:
            if not df_e.empty:
                st.subheader("Análisis de Eb/No")
                fig_ebno = px.scatter(df_e, x='Estación', y='Eb/No Promedio (dB)', color='Tipo',
                                     title="Niveles de Eb/No detectados",
                                     height=500)
                fig_ebno.add_hline(y=8.0, line_dash="dash", line_color="red", annotation_text="Umbral Crítico")
                st.plotly_chart(fig_ebno, use_container_width=True)
                
                st.dataframe(df_e, use_container_width=True, hide_index=True)
            else:
                st.warning("No se detectaron datos de Eb/No válidos en el archivo de estadísticas.")

else:
    st.info("Por favor, sube ambos archivos para iniciar el análisis.")
