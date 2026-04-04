import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(page_title="Meru AI - Data Analysis", layout="wide")

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

# Inicializar DB
init_db()

# --- APP LOGIC ---
st.title("🛰️ Meru Networks AI Suite")

# Sidebar para carga de archivos e Historial
with st.sidebar:
    st.header("Configuración y Carga")
    uploaded_usage = st.file_uploader("Cargar Reporte de Uso (.csv)", type="csv", key="usage")
    uploaded_stats = st.file_uploader("Cargar Estadísticas Eb/No (.csv)", type="csv", key="stats")
    
    st.divider()
    if st.button("Limpiar Historial"):
        conn = sqlite3.connect('meru_history.db')
        conn.cursor().execute("DELETE FROM history")
        conn.commit()
        conn.close()
        st.success("Historial eliminado")
        st.rerun()

# Pestañas principales
tab_analysis, tab_history = st.tabs(["📊 Análisis Actual", "📜 Historial de Datos"])

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

with tab_analysis:
    if uploaded_usage and uploaded_stats:
        if st.button("🚀 INICIAR ANÁLISIS IA", use_container_width=True):
            try:
                # Procesar Uso
                usage_df = pd.read_csv(uploaded_usage, skiprows=3)
                # Procesar Stats
                stats_df = pd.read_csv(uploaded_stats)
                
                latest_stats = stats_df.iloc[-1]
                latest_usage = usage_df.iloc[-1]
                
                # Identificar anomalías de Eb/No
                anomalies = []
                for col in stats_df.columns:
                    if "Eb/No" in col:
                        try:
                            val = float(latest_stats[col])
                            if val < 10.0:
                                anomalies.append({
                                    "node": col.split('/')[0].replace('"', ''),
                                    "value": val,
                                    "type": "Eb/No Bajo"
                                })
                        except: continue

                # Tráfico
                numeric_usage = pd.to_numeric(latest_usage, errors='coerce').fillna(0)
                total_traffic = round(numeric_usage.sum() / 1024, 2)
                
                analysis_result = {
                    "success": True,
                    "total_traffic": total_traffic,
                    "anomalies": anomalies,
                    "node_count": len(usage_df.columns) - 1,
                    "top_nodes": numeric_usage.sort_values(ascending=False).head(10).to_dict()
                }
                
                st.session_state.current_analysis = analysis_result
                # Guardar en DB
                save_to_history(total_traffic, analysis_result["node_count"], len(anomalies), analysis_result)
                st.success("Análisis completado y guardado en base de datos.")
            
            except Exception as e:
                st.error(f"Error procesando archivos: {e}")
    else:
        st.info("Por favor, sube ambos archivos CSV en el panel lateral para habilitar el botón de análisis.")

    # Renderizado del Dashboard (si existe análisis)
    if st.session_state.current_analysis:
        path_to_html = "index.html"
        if os.path.exists(path_to_html):
            with open(path_to_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Inyectar datos en el HTML
            analysis_data = json.dumps(st.session_state.current_analysis)
            full_html = html_content.replace("window.ANALYSIS_DATA = null;", f"window.ANALYSIS_DATA = {analysis_data};")
            components.html(full_html, height=700, scrolling=True)

with tab_history:
    history_df = get_history()
    if not history_df.empty:
        st.subheader("Registros almacenados")
        # Mostrar tabla resumida
        st.dataframe(history_df[["timestamp", "traffic_gb", "node_count", "anomaly_count"]], use_container_width=True)
        
        # Selección para ver detalles
        selected_id = st.selectbox("Seleccionar registro para ver detalle:", history_df["id"])
        if selected_id:
            row = history_df[history_df["id"] == selected_id].iloc[0]
            details = json.loads(row["details"])
            st.json(details)
    else:
        st.write("No hay registros en la base de datos.")

# CSS para mejorar estética
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)
