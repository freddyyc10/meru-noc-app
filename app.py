import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json
import time
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE API IA ---
apiKey = ""

def call_gemini_analysis(data_content, is_csv=False):
    """Llamada a Gemini 2.5 Flash para análisis de red y datos CSV"""
    if is_csv:
        system_prompt = (
            "Eres el Analista Senior de Datos de Meru NOC. Tu tarea es analizar el archivo CSV cargado, "
            "identificar anomalías en los parámetros de red (EbNo, Latencia, Pérdida de Paquetes) y "
            "proporcionar un resumen ejecutivo con recomendaciones técnicas de optimización."
        )
        user_query = f"ANALIZA ESTOS DATOS DE ARCHIVO CSV: \n{data_content}\n. Genera un reporte detallado:"
    else:
        system_prompt = (
            "Eres el Ingeniero de IA de Meru NOC. Analiza la telemetría actual y sugiere mitigación si EbNo < 10."
        )
        user_query = f"REPORTE DE TELEMETRÍA: {data_content}. Diagnóstico técnico:"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Análisis completado.")
            time.sleep(2**i)
        except Exception:
            time.sleep(2**i)
    return "⚠️ Error de conexión con el motor de IA."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru NOC - AI Master", page_icon="🛰️", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #e6edf3; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
    .csv-container { border: 1px solid #388bfd; border-radius: 10px; padding: 20px; background-color: #0d1117; }
    .ai-response { background-color: #1c2128; border-left: 5px solid #388bfd; padding: 20px; border-radius: 5px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- BARRA LATERAL (IMPORTACIÓN CSV) ---
    st.sidebar.image("Meru Networks JPG Horizontal.jpg", width=180) if os.path.exists("Meru Networks JPG Horizontal.jpg") else st.sidebar.title("MERU NOC")
    st.sidebar.header("📁 Importar Datos")
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV de telemetría", type=["csv"])
    
    # --- ENCABEZADO ---
    col_h1, col_h2 = st.columns([1, 4])
    with col_h1:
        if os.path.exists("Meru Networks JPG Horizontal.jpg"):
            st.image("Meru Networks JPG Horizontal.jpg", width=150)
    with col_h2:
        st.title("Meru Intelligence Center")
        st.caption("Sistema de Monitoreo Proactivo con Inteligencia Artificial")

    st.divider()

    if uploaded_file is not None:
        # --- PROCESAMIENTO DE ARCHIVO SUBIDO ---
        try:
            df_csv = pd.read_csv(uploaded_file)
            st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Vista Previa de Datos")
                st.dataframe(df_csv.head(10), use_container_width=True)
                
                if st.checkbox("Mostrar estadísticas descriptivas"):
                    st.write(df_csv.describe())

            with col2:
                st.subheader("🧠 Análisis de IA del CSV")
                if st.button("Analizar CSV con IA", use_container_width=True):
                    with st.spinner("La IA está leyendo y analizando el archivo..."):
                        # Enviamos una muestra representativa (cabecera y estadisticas) para no saturar el prompt
                        csv_sample = df_csv.describe().to_string() + "\n" + df_csv.head(20).to_string()
                        analysis = call_gemini_analysis(csv_sample, is_csv=True)
                        st.markdown(f'<div class="ai-response">{analysis}</div>', unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📈 Gráfico de Tendencias (CSV)")
            numeric_cols = df_csv.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                col_sel1 = st.selectbox("Eje X", options=df_csv.columns)
                col_sel2 = st.selectbox("Eje Y (Métrica)", options=numeric_cols)
                fig_csv = px.line(df_csv, x=col_sel1, y=col_sel2, markers=True, template="plotly_dark")
                st.plotly_chart(fig_csv, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al procesar el CSV: {e}")

    else:
        # --- VISTA POR DEFECTO (SIN ARCHIVO) ---
        st.info("💡 Sube un archivo CSV en la barra lateral para iniciar el análisis profundo de datos.")
        
        # Datos simulados para mantener el dashboard vivo
        df_sim = pd.DataFrame({
            'Minutos': list(range(60)),
            'EbNo': np.random.normal(12, 0.5, 60)
        })
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Eb/No Actual", f"{df_sim['EbNo'].iloc[-1]:.2f} dB", "0.2")
        c2.metric("Nodos Activos", "124/125", "-1")
        c3.metric("Uptime Global", "99.98%", "0.01%")
        
        st.plotly_chart(px.area(df_sim, x='Minutos', y='EbNo', title="Señal Satelital (Simulada)", template="plotly_dark"), use_container_width=True)

if __name__ == "__main__":
    main()
