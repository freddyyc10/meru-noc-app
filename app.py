import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Meru AI - Database & Analysis", layout="wide")

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
    st.header("📥 Importar Archivos CSV")
    st.markdown("Cargue los reportes exportados de la plataforma VNO.")
    
    uploaded_usage = st.file_uploader("1. Reporte de Uso (Traffic)", type="csv", help="Archivo: VNO Meru-Networks Data Usage...")
    uploaded_stats = st.file_uploader("2. Estadísticas Eb/No (Quality)", type="csv", help="Archivo: statistics (XX).csv")
    
    st.divider()
    st.subheader("⚙️ Gestión de Datos")
    if st.button("🗑️ Borrar Historial de BD"):
        conn = sqlite3.connect('meru_history.db')
        conn.cursor().execute("DELETE FROM history")
        conn.commit()
        conn.close()
        st.warning("Historial eliminado de la base de datos.")
        st.rerun()

# Tabs
tab_analysis, tab_history = st.tabs(["📊 Análisis en Tiempo Real", "📜 Historial de Base de Datos"])

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

with tab_analysis:
    if uploaded_usage and uploaded_stats:
        st.success("Archivos listos para procesar.")
        if st.button("🚀 PROCESAR E IMPORTAR A HISTORIAL", use_container_width=True):
            try:
                # 1. Procesar Reporte de Uso (Saltando encabezados de metadata de Meru)
                usage_df = pd.read_csv(uploaded_usage, skiprows=3)
                # Eliminar columna Date para cálculos
                if 'Date' in usage_df.columns:
                    usage_data_only = usage_df.drop(columns=['Date'])
                else:
                    usage_data_only = usage_df
                
                # Obtener última fila (más reciente)
                latest_usage_row = usage_data_only.iloc[-1]
                # Convertir a numérico y limpiar
                numeric_usage = pd.to_numeric(latest_usage_row, errors='coerce').fillna(0)
                
                # 2. Procesar Estadísticas Eb/No
                stats_df = pd.read_csv(uploaded_stats)
                latest_stats = stats_df.iloc[-1]
                
                anomalies = []
                for col in stats_df.columns:
                    if "Eb/No" in col:
                        try:
                            val = float(latest_stats[col])
                            if 0.1 < val < 10.0: # Evitar ceros absolutos como anomalía si es desconexión
                                anomalies.append({
                                    "node": col.split('/')[0].replace('"', ''),
                                    "value": val,
                                    "type": "Eb/No Crítico"
                                })
                        except: continue

                # Totales
                total_traffic_gb = round(numeric_usage.sum() / 1024, 2)
                node_count = len(numeric_usage)
                
                # Top Nodes (filtrando Date si aparece)
                top_nodes = numeric_usage.sort_values(ascending=False).head(10).to_dict()

                analysis_result = {
                    "success": True,
                    "total_traffic": total_traffic_gb,
                    "anomalies": anomalies,
                    "node_count": node_count,
                    "top_nodes": top_nodes
                }
                
                st.session_state.current_analysis = analysis_result
                save_to_history(total_traffic_gb, node_count, len(anomalies), analysis_result)
                st.balloons()
            
            except Exception as e:
                st.error(f"Error en procesamiento: {e}")
    else:
        st.info("Utilice el panel lateral para importar los archivos CSV de Meru.")

    if st.session_state.current_analysis:
        path_to_html = "index.html"
        if os.path.exists(path_to_html):
            with open(path_to_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            analysis_data = json.dumps(st.session_state.current_analysis)
            full_html = html_content.replace("window.ANALYSIS_DATA = null;", f"window.ANALYSIS_DATA = {analysis_data};")
            components.html(full_html, height=750, scrolling=False)

with tab_history:
    st.subheader("Historial de Análisis Guardados")
    history_df = get_history()
    if not history_df.empty:
        st.dataframe(history_df[["id", "timestamp", "traffic_gb", "node_count", "anomaly_count"]], use_container_width=True)
        
        selected_id = st.number_input("Ver detalles del ID:", min_value=int(history_df['id'].min()), max_value=int(history_df['id'].max()))
        if st.button("Cargar detalle histórico"):
            row = history_df[history_df["id"] == selected_id].iloc[0]
            st.session_state.current_analysis = json.loads(row["details"])
            st.info(f"Mostrando datos del registro {selected_id} en la pestaña de Análisis.")
    else:
        st.write("La base de datos está vacía. Importe archivos para generar un historial.")
