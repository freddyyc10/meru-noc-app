import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import json
import time

# --- CONFIGURACIÓN DE API IA ---
# Clave proporcionada por el usuario
apiKey = "AIzaSyBQy0psFsocJJNn5rEsiYRCi-dqOH_qDmg" 
# Usando el modelo estable 1.5-flash para evitar el error 404
MODEL_NAME = "gemini-1.5-flash"

def call_gemini_analysis(data_content):
    """Llamada a Gemini 1.5 Flash para análisis técnico de NOC"""
    
    if not apiKey:
        return "❌ Error: API Key no configurada."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={apiKey}"
    
    system_prompt = (
        "Eres el sistema experto de Meru Intelligence Center. Tu especialidad es la telemetría satelital y de redes. "
        "Analiza los siguientes datos de un archivo CSV de monitoreo (NOC). Busca saturación de ancho de banda, "
        "caídas de Eb/No, fluctuaciones de latencia o pérdida de paquetes. "
        "Responde con un informe técnico estructurado en: 1. Resumen de Salud, 2. Anomalías Detectadas, 3. Recomendaciones."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": f"SISTEMA: {system_prompt}\n\nDATOS A ANALIZAR:\n{data_content}"}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    # Reintentos con backoff exponencial
    for i in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 404:
                return f"⚠️ Error 404: El modelo '{MODEL_NAME}' no fue encontrado. Verifica la disponibilidad en tu región o cuenta de Google AI Studio."
            elif response.status_code == 429:
                time.sleep(2**i)
                continue
            else:
                return f"⚠️ Error de API ({response.status_code}): {response.text}"
        except Exception as e:
            return f"⚠️ Excepción de conexión: {str(e)}"
    
    return "Error: Máximo de reintentos alcanzado."

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Meru NOC - AI Master", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .report-container { 
        background-color: #1c2128; 
        border-left: 5px solid #238636; 
        padding: 25px; 
        border-radius: 10px;
        color: #e6edf3;
        font-family: sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Meru Intelligence Center")
st.subheader("Monitoreo Proactivo de Red con IA")

# Sidebar
st.sidebar.header("📁 Importar Datos")
uploaded_file = st.sidebar.file_uploader("Cargar statistics (44).csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Archivo cargado correctamente")
    
    tab_viz, tab_ai = st.tabs(["📊 Visualización", "🧠 Análisis Predictivo"])
    
    with tab_viz:
        st.write("### Vista Previa de Telemetría")
        st.dataframe(df.head(10), use_container_width=True)
        
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                feat = st.selectbox("Métrica Primaria", num_cols, index=0)
                fig1 = px.line(df, y=feat, title=f"Tendencia de {feat}", template="plotly_dark")
                st.plotly_chart(fig1, use_container_width=True)
            with col_chart2:
                feat2 = st.selectbox("Métrica Secundaria", num_cols, index=min(1, len(num_cols)-1))
                fig2 = px.histogram(df, x=feat2, title=f"Distribución de {feat2}", template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)

    with tab_ai:
        st.write("### Informe de Inteligencia Artificial")
        
        if st.button("🚀 Ejecutar Diagnóstico con Gemini"):
            with st.spinner("Analizando patrones de red..."):
                # Preparar datos: Estadísticas + Muestra representativa
                stats = df.describe().to_string()
                # Tomamos las 20 filas con valores más altos en la primera columna numérica (posibles picos)
                # y las primeras/últimas filas.
                sample_data = df.head(15).to_string()
                
                context = f"ESTADÍSTICAS DESCRIPTIVAS:\n{stats}\n\nMUESTRA DE DATOS:\n{sample_data}"
                
                report = call_gemini_analysis(context)
                
                st.markdown(f'<div class="report-container">{report}</div>', unsafe_allow_html=True)
                st.download_button("Descargar Reporte", report, file_name="diagnostico_noc.md")
else:
    st.info("Por favor, carga el archivo CSV en la barra lateral para comenzar el análisis.")
