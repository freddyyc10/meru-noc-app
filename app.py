import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# Configuración de nivel profesional
st.set_page_config(page_title="Meru VNO Expert Analytics", layout="wide")

# --- CSS de alta fidelidad ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-critical { color: #dc3545; font-weight: bold; }
    .status-optimal { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def clean_station_name(name):
    """Extrae el ID base de la estación ignorando sufijos de iDirect."""
    if not isinstance(name, str): return name
    # Elimina '/FL...', '/RL...', ' In', ' Out' y comillas
    clean = re.sub(r'(/.*| In| Out|")', '', name).strip()
    return clean

def load_usage_data(file):
    """Procesador robusto para Data Usage Report (20)."""
    content = file.getvalue().decode('utf-8').splitlines()
    # Buscar la línea que contiene "Date" para iniciar el DF
    start_line = 0
    for i, line in enumerate(content[:10]):
        if "Date" in line:
            start_line = i
            break
    
    df = pd.read_csv(io.StringIO("\n".join(content[start_line:])))
    
    # Derretir el dataframe para tener Estación | Tráfico
    traffic_cols = [c for c in df.columns if c != "Date"]
    df_melted = df.melt(id_vars=["Date"], value_vars=traffic_cols, var_name="Raw_Name", value_name="MB")
    
    df_melted['Estacion'] = df_melted['Raw_Name'].apply(clean_station_name)
    df_melted['MB'] = pd.to_numeric(df_melted['MB'], errors='coerce').fillna(0)
    
    # Agrupar por estación
    return df_melted.groupby('Estacion')['MB'].sum().reset_index()

def load_stats_data(file):
    """Procesador experto para Statistics (44)."""
    df = pd.read_csv(file)
    # Limpiar nombres de columnas (quitar comillas de iDirect)
    df.columns = [c.replace('"', '') for c in df.columns]
    
    stats_summary = []
    
    # Identificar columnas de FL y RL
    for col in df.columns:
        if col == "Date (UTC)": continue
        
        station = clean_station_name(col)
        values = pd.to_numeric(df[col], errors='coerce').dropna()
        
        if len(values) > 0:
            stats_summary.append({
                'Estacion': station,
                'Tipo': 'FL' if 'FL' in col else 'RL',
                'Avg': values.mean(),
                'Min': values.min(),
                'P10': values.quantile(0.1) # Percentil 10 para detectar caídas reales
            })
            
    if not stats_summary: return pd.DataFrame()
    
    df_stats = pd.DataFrame(stats_summary)
    # Pivotar para tener FL y RL en la misma fila por estación
    df_pivot = df_stats.pivot_table(index='Estacion', columns='Tipo', values=['Avg', 'P10']).reset_index()
    
    # Aplanar columnas multinivel
    df_pivot.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in df_pivot.columns]
    return df_pivot

# --- INTERFAZ PRINCIPAL ---
st.title("🛰️ Sistema de Diagnóstico de Red Meru VNO")
st.subheader("Nivel: Ingeniería de Redes / NOC")

col1, col2 = st.columns(2)
with col1:
    usage_file = st.file_uploader("Subir 'Data Usage Report (20)'", type="csv")
with col2:
    stats_file = st.file_uploader("Subir 'Statistics (44)' (Eb/No)", type="csv")

if usage_file and stats_file:
    with st.spinner("Procesando telemetría..."):
        df_usage = load_usage_data(usage_file)
        df_stats = load_stats_data(stats_file)
        
        if not df_stats.empty:
            # Join de nivel experto (Inner para asegurar que solo analizamos estaciones con data completa)
            merged = pd.merge(df_usage, df_stats, on="Estacion", how="inner")
            
            # --- KPI de Alto Nivel ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Estaciones", len(merged))
            m2.metric("Tráfico Total", f"{merged['MB'].sum()/1024:.2f} GB")
            m3.metric("Promedio FL", f"{merged['FL_Avg'].mean():.1f} dB")
            m4.metric("Estaciones en Riesgo", len(merged[merged['FL_P10'] < 9.0]))

            # --- Visualización Avanzada ---
            t1, t2 = st.tabs(["📊 Correlación Señal/Tráfico", "⚠️ Diagnóstico de Fallas"])
            
            with t1:
                fig = px.scatter(merged, x="MB", y="FL_Avg", 
                                 size="MB", color="RL_Avg",
                                 hover_name="Estacion",
                                 title="Análisis de Eficiencia Espectral (MB vs Eb/No)",
                                 labels={"FL_Avg": "Forward Link (dB)", "MB": "Consumo (MB)", "RL_Avg": "Return Link"},
                                 color_continuous_scale="Viridis")
                fig.add_hline(y=9.5, line_dash="dash", line_color="red", annotation_text="Umbral Crítico FL")
                st.plotly_chart(fig, use_container_width=True)

            with t2:
                st.write("### Estaciones con Degradación de Señal")
                # Filtrar estaciones críticas
                criticas = merged[merged['FL_P10'] < 9.5].sort_values('FL_P10')
                
                if not criticas.empty:
                    # Crear tabla de diagnóstico
                    diag_df = criticas.copy()
                    diag_df['Estado'] = diag_df['FL_P10'].apply(lambda x: "🔴 CRÍTICO" if x < 8.5 else "🟡 DEGRADADO")
                    diag_df['Recomendación'] = diag_df['FL_Avg'].apply(lambda x: "Revisar Apuntamiento" if x < 10 else "Posible Interferencia/Clima")
                    
                    st.table(diag_df[['Estacion', 'FL_Avg', 'FL_P10', 'RL_Avg', 'MB', 'Estado', 'Recomendación']])
                else:
                    st.success("✅ No se detectan estaciones bajo el umbral crítico en este reporte.")

            # --- Exportación ---
            csv = merged.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte Consolidado", csv, "consolidado_vno.csv", "text/csv")
        else:
            st.error("No se pudieron cruzar los datos. Verifique que los archivos corresponden al mismo VNO.")
else:
    st.info("Por favor, cargue ambos archivos CSV para iniciar el análisis.")
