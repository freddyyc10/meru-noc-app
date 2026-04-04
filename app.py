import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import streamlit.components.v1 as components

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Meru AI - Data Analysis", layout="wide", initial_sidebar_state="collapsed")

def process_csv_files():
    """Procesa los archivos CSV subidos para extraer métricas clave."""
    try:
        # 1. Procesar Reporte de Uso (Saltar 3 líneas de encabezado)
        usage_file = "VNO Meru-Networks Data Usage Report (20).csv"
        usage_df = pd.read_csv(usage_file, skiprows=3)
        
        # 2. Procesar Estadísticas (Eb/No)
        stats_file = "statistics (44).csv"
        stats_df = pd.read_csv(stats_file)
        
        # Obtener la última fila (datos más recientes)
        latest_usage = usage_df.iloc[-1]
        latest_stats = stats_df.iloc[-1]
        
        # Limpieza de datos: Identificar nodos con problemas de Eb/No (< 10)
        anomalies = []
        for col in stats_df.columns:
            if "Eb/No" in col:
                val = latest_stats[col]
                # Manejar valores nulos o vacíos
                try:
                    val_float = float(val)
                    if val_float < 10.0:
                        node_name = col.split('/')[0].replace('"', '')
                        anomalies.append({
                            "node": node_name,
                            "value": val_float,
                            "type": "Eb/No Bajo",
                            "severity": "CRITICAL" if val_float < 8 else "WARNING"
                        })
                except:
                    continue

        # Calcular Tráfico Total (Solo columnas numéricas)
        numeric_usage = pd.to_numeric(latest_usage, errors='coerce').fillna(0)
        total_traffic_gb = round(numeric_usage.sum() / 1024, 2)
        
        # Preparar datos para el gráfico (Top 8 nodos con más consumo)
        top_usage = numeric_usage.sort_values(ascending=False).head(8)
        chart_labels = [str(i) for i in top_usage.index]
        chart_values = top_usage.values.tolist()

        return {
            "success": True,
            "total_traffic": total_traffic_gb,
            "anomalies": anomalies[:10], # Mostrar top 10 anomalías
            "node_count": len(usage_df.columns) - 1,
            "chart_labels": chart_labels,
            "chart_values": chart_values
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Estilos CSS para ocultar elementos de Streamlit
st.markdown("""
    <style>
        .main .block-container { padding: 0; }
        iframe { border: none; }
        #MainMenu, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# Lógica del Dashboard
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Renderizado del componente HTML
path_to_html = "index.html"
if os.path.exists(path_to_html):
    with open(path_to_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Inyectar estado actual
    analysis_data = json.dumps(st.session_state.analysis_result)
    full_html = html_content.replace("window.ANALYSIS_DATA = null;", f"window.ANALYSIS_DATA = {analysis_data};")
    
    # Manejar el evento de clic del botón desde el HTML
    # Nota: Usamos un truco de Streamlit para detectar el clic mediante un parámetro de consulta o un componente
    res = components.html(full_html, height=850, scrolling=False)
    
    # Botón invisible de Streamlit para procesar (disparado por el usuario en la UI real si fuera necesario)
    # En este entorno, simulamos la respuesta del botón directamente
    if st.button("Ejecutar Análisis de IA"):
        st.session_state.analysis_result = process_csv_files()
        st.rerun()
else:
    st.error("No se encontró el archivo index.html")
