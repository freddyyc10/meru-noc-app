import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Meru AI - Analizador de Red", layout="wide")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('meru_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  traffic_gb REAL, 
                  node_count INTEGER, 
                  anomaly_count INTEGER,
                  details TEXT)''')
    conn.commit()
    conn.close()

def save_to_history(traffic, nodes, anomalies, raw_details):
    conn = sqlite3.connect('meru_history.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (timestamp, traffic_gb, node_count, anomaly_count, details) VALUES (?, ?, ?, ?, ?)",
              (timestamp, traffic, nodes, anomalies, json.dumps(raw_details)))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('meru_history.db')
    df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC", conn)
    conn.close()
    return df

init_db()

# --- APP LOGIC ---
st.title("🛰️ Meru Networks AI Suite")

# Sidebar
with st.sidebar:
    st.header("📥 Importar Archivos Meru")
    st.markdown("Cargue los reportes exportados directamente.")
    
    uploaded_usage = st.file_uploader("1. Reporte de Uso (Data Usage)", type="csv")
    uploaded_stats = st.file_uploader("2. Estadísticas (Eb/No)", type="csv")
    
    st.divider()
    if st.button("🗑️ Limpiar Base de Datos"):
        conn = sqlite3.connect('meru_history.db')
        conn.cursor().execute("DELETE FROM history")
        conn.commit()
        conn.close()
        st.rerun()

# Tabs
tab_analysis, tab_history = st.tabs(["📊 Dashboard de Análisis", "📜 Historial Guardado"])

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

with tab_analysis:
    if uploaded_usage and uploaded_stats:
        if st.button("🚀 ANALIZAR DATOS IMPORTADOS", use_container_width=True):
            try:
                # 1. PROCESAR DATA USAGE
                # El archivo tiene 3 líneas de encabezado (Report Name, Units, etc)
                usage_df = pd.read_csv(uploaded_usage, skiprows=3)
                
                # Identificar columnas de datos (excluyendo 'Date')
                data_cols = [c for c in usage_df.columns if c.lower() != 'date']
                
                # Obtener la última fila con datos válidos
                latest_usage = usage_df.iloc[-1]
                
                # Convertir a numérico, forzando errores a 0 y sumando
                usage_series = pd.to_numeric(latest_usage[data_cols], errors='coerce').fillna(0)
                total_mb = usage_series.sum()
                total_gb = round(total_mb / 1024, 2)
                
                # Top Nodes (Combinando In/Out para el nombre)
                top_data = usage_series.sort_values(ascending=False).head(15).to_dict()

                # 2. PROCESAR ESTADÍSTICAS (Eb/No)
                stats_df = pd.read_csv(uploaded_stats)
                # Limpiar nombres de columnas (quitar comillas si existen)
                stats_df.columns = [c.replace('"', '').strip() for c in stats_df.columns]
                
                latest_stats = stats_df.iloc[-1]
                
                anomalies = []
                for col in stats_df.columns:
                    if "Eb/No" in col:
                        try:
                            val = float(latest_stats[col])
                            # Criterio: Menor a 7 es crítico en Meru para estabilidad
                            if 0 < val < 8.0:
                                anomalies.append({
                                    "node": col.split('/')[0],
                                    "value": val,
                                    "type": "Eb/No Bajo"
                                })
                        except: continue

                # Preparar resultado
                analysis_result = {
                    "success": True,
                    "total_traffic": total_gb,
                    "anomalies": anomalies,
                    "node_count": len(data_cols),
                    "top_nodes": top_data
                }
                
                st.session_state.current_analysis = analysis_result
                save_to_history(total_gb, len(data_cols), len(anomalies), analysis_result)
                st.success("Análisis completado exitosamente.")
            
            except Exception as e:
                st.error(f"Error procesando los archivos: {str(e)}")
                st.info("Asegúrese de que los archivos sean los exportados originales de la plataforma.")

    if st.session_state.current_analysis:
        path_to_html = "index.html"
        if os.path.exists(path_to_html):
            with open(path_to_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            analysis_data = json.dumps(st.session_state.current_analysis)
            full_html = html_content.replace("window.ANALYSIS_DATA = null;", f"window.ANALYSIS_DATA = {analysis_data};")
            components.html(full_html, height=800, scrolling=False)
    else:
        st.info("Por favor, suba los archivos CSV en el panel lateral para comenzar el análisis.")

with tab_history:
    history_df = get_history()
    if not history_df.empty:
        st.subheader("Registros en Base de Datos")
        st.dataframe(history_df[["id", "timestamp", "traffic_gb", "node_count", "anomaly_count"]], use_container_width=True)
        
        selected_id = st.selectbox("Seleccionar ID para ver detalle:", history_df['id'])
        if st.button("Recuperar este análisis"):
            row = history_df[history_df["id"] == selected_id].iloc[0]
            st.session_state.current_analysis = json.loads(row["details"])
            st.rerun()
    else:
        st.write("No hay datos históricos aún.")
