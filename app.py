import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json
import time
import os

# --- CONFIGURACIÓN DE API IA ---
# Clave proporcionada para Gemini
apiKey = "AIzaSyBQy0psFsocJJNn5rEsiYRCi-dqOH_qDmg" 

def call_gemini_analysis(data_content, is_csv=False):
    """Llamada a Gemini 2.5 Flash para análisis de red y datos CSV"""
    
    if not apiKey:
        return "❌ Error: No se ha configurado la API Key de Google Gemini."

    if is_csv:
        system_prompt = (
            "Eres el Analista Senior de Datos de Meru NOC (Teleport/Satellite Network). "
            "Tu tarea es analizar el archivo CSV cargado, identificar anomalías en los parámetros "
            "de red (Eb/No, Es/No, Latencia, Packet Loss, Jitter) y proporcionar un resumen ejecutivo "
            "con recomendaciones técnicas de optimización y posibles causas de degradación."
        )
        user_query = f"ANALIZA ESTOS DATOS DE TELEMETRÍA (CSV): \n{data_content}\n. Genera un reporte técnico para el equipo de NOC:"
    else:
        system_prompt = "Eres el Ingeniero de IA de Meru NOC. Analiza la telemetría actual."
        user_query = f"REPORTE: {data_content}."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    # Implementación de reintentos con backoff exponencial
    for i in range(5):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=40)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Análisis completado sin respuesta de texto.")
            elif response.status_code == 429:
                time.sleep(2**i)
                continue
            else:
                return f"⚠️ Error del motor de IA ({response.status_code}): {response.text}"
        except Exception as e:
            time.sleep(2**i)
            error_msg = str(e)
    
    return f"⚠️ Error de conexión: {error_msg}"

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru NOC - AI Master", page_icon="🛰️", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #e6edf3; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .ai-response { 
        background-color: #1c2128; 
        border-left: 5px solid #238636; 
        padding: 20px; 
        border-radius: 8px; 
        margin-top: 20px;
        color: #e6edf3;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    .status-card {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- BARRA LATERAL ---
    st.sidebar.title("🛰️ Meru NOC")
    st.sidebar.markdown("---")
    st.sidebar.header("📁 Importar Datos")
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV de telemetría (iDirect/Sat)", type=["csv"])
    
    # --- HEADER ---
    col_logo, col_title = st.columns([1, 5])
    with col_title:
        st.title("Meru Intelligence Center")
        st.caption("Dashboard de Monitoreo Proactivo con IA (Gemini 2.5 Flash)")

    st.divider()

    if uploaded_file is not None:
        try:
            # Lectura del CSV
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")
            
            # Layout principal con CSV cargado
            tab1, tab2 = st.tabs(["📊 Visualización de Datos", "🧠 Diagnóstico IA"])
            
            with tab1:
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                col_stat1.metric("Total Registros", len(df))
                
                # Intentar detectar columnas numéricas clave automáticamente
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                with st.expander("Ver tabla completa de datos"):
                    st.dataframe(df, use_container_width=True)
                
                if numeric_cols:
                    st.subheader("📈 Análisis de Tendencias")
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        y_axis = st.selectbox("Seleccionar Métrica", options=numeric_cols)
                        x_axis = st.selectbox("Eje Temporal / Índice", options=df.columns)
                    with c2:
                        fig = px.line(df, x=x_axis, y=y_axis, title=f"Evolución de {y_axis}", template="plotly_dark")
                        fig.update_traces(line_color='#58a6ff')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No se encontraron columnas numéricas para graficar.")

            with tab2:
                st.subheader("Análisis Predictivo y de Salud")
                st.info("La IA analizará las tendencias, estadísticas y anomalías dentro de los datos cargados.")
                
                if st.button("🚀 Iniciar Diagnóstico de Red con IA"):
                    with st.spinner("Gemini está procesando la telemetría..."):
                        # Extraemos una muestra representativa para no exceder límites de tokens
                        # pero manteniendo la esencia estadística
                        stats_summary = df.describe().to_string()
                        head_sample = df.head(15).to_string()
                        tail_sample = df.tail(15).to_string()
                        
                        data_payload = f"ESTADÍSTICAS GENERALES:\n{stats_summary}\n\nMUESTRA INICIAL:\n{head_sample}\n\nMUESTRA FINAL:\n{tail_sample}"
                        
                        analysis_result = call_gemini_analysis(data_payload, is_csv=True)
                        
                        st.markdown(f"""
                        <div class="ai-response">
                            <h3 style='margin-top:0;'>Reporte de Inteligencia Meru NOC</h3>
                            {analysis_result}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Opción para descargar reporte
                        st.download_button("Descargar Reporte IA", analysis_result, file_name="reporte_ia_meru.txt")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
    else:
        # Estado inicial si no hay archivo
        st.warning("Esperando carga de datos de telemetría (CSV) en la barra lateral...")
        
        # Dashboard demo simplificado
        c1, c2, c3 = st.columns(3)
        c1.metric("Status Teleport", "ONLINE", delta="Stable")
        c2.metric("Nodos en Alerta", "0", delta="0")
        c3.metric("Promedio Eb/No (Pool)", "11.5 dB")
        
        # Simulación visual
        chart_data = pd.DataFrame(np.random.randn(20, 1), columns=['EbNo'])
        st.line_chart(chart_data)

if __name__ == "__main__":
    main()
