import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
import re
import io

# Configuración de página
st.set_page_config(page_title="Meru VNO - Inteligencia de Red", layout="wide")

# --- Estilos ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .report-container { 
        background-color: white; 
        padding: 30px; 
        border-radius: 12px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 6px solid #007bff;
    }
    .metric-card {
        text-align: center;
        padding: 15px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Configuración de API Gemini ---
apiKey = "" 

def get_gemini_analysis(prompt_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres un experto en operaciones de satélite (NOC). Analiza el consumo y niveles Eb/No. Identifica desapuntamientos, lluvia o congestión. Responde en español de forma técnica y profesional."}]
        }
    }
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except: time.sleep(delay)
    return "Error al procesar el análisis con IA."

# --- Procesador de Datos ---
def parse_files(usage_file, stats_ebno_file, stats_traffic_file):
    try:
        # 1. Cargar Reporte de Uso (MBytes)
        # Saltamos 3 líneas como indica el archivo
        usage_content = usage_file.getvalue().decode('utf-8')
        df_usage_raw = pd.read_csv(io.StringIO(usage_content), skiprows=3)
        
        usage_results = []
        for col in df_usage_raw.columns:
            if " In" in col:
                station = col.replace(" In", "").strip()
                out_col = f"{station} Out"
                in_val = pd.to_numeric(df_usage_raw[col], errors='coerce').sum()
                out_val = pd.to_numeric(df_usage_raw[out_col], errors='coerce').sum() if out_col in df_usage_raw.columns else 0
                usage_results.append({"Estación": station, "In_MB": in_val, "Out_MB": out_val, "Total_MB": in_val + out_val})
        
        df_usage = pd.DataFrame(usage_results).sort_values("Total_MB", ascending=False)

        # 2. Cargar Statistics (Eb/No) - Archivo 44
        df_ebno_raw = pd.read_csv(stats_ebno_file)
        ebno_results = []
        for col in df_ebno_raw.columns:
            if "/" in col and "Eb/No" in col:
                parts = col.split("/")
                station = parts[0].replace('"', '').strip()
                metric_type = "RL" if "RL" in parts[1] else "FL"
                vals = pd.to_numeric(df_ebno_raw[col], errors='coerce').dropna()
                if not vals.empty:
                    ebno_results.append({
                        "Estación": station,
                        "Tipo": metric_type,
                        "Avg_EbNo": vals.mean(),
                        "Min_EbNo": vals.min()
                    })
        df_ebno = pd.DataFrame(ebno_results)

        # 3. Consolidación
        # Pivotamos EbNo para tener RL y FL en la misma fila
        if not df_ebno.empty:
            df_ebno_pivot = df_ebno.pivot(index="Estación", columns="Tipo", values="Avg_EbNo").reset_index()
            df_final = pd.merge(df_usage, df_ebno_pivot, on="Estación", how="left")
        else:
            df_final = df_usage

        return df_final
    except Exception as e:
        st.error(f"Error procesando archivos: {e}")
        return None

# --- UI INTERFACE ---
st.title("🛰️ Panel de Diagnóstico VNO Meru")

col_input, col_info = st.columns([1, 2])

with col_input:
    st.subheader("Carga de Reportes")
    f_usage = st.file_uploader("1. Usage Report (20).csv", type="csv")
    f_ebno = st.file_uploader("2. Statistics (44) - Eb/No", type="csv")
    f_traffic = st.file_uploader("3. Statistics (45) - Traffic", type="csv")
    btn_analizar = st.button("🚀 Iniciar Análisis Inteligente", use_container_width=True)

if f_usage and f_ebno and f_traffic:
    data = parse_files(f_usage, f_ebno, f_traffic)
    
    if data is not None:
        if btn_analizar:
            # Preparar contexto para IA
            resumen_data = data.sort_values("Total_MB", ascending=False).head(15).to_string()
            criticos = data[data['FL'] < 9.5].to_string() if 'FL' in data.columns else "No detectados"
            
            prompt = f"""
            Analiza los siguientes datos de la red Meru:
            
            RESUMEN TOP CONSUMO (MBytes):
            {resumen_data}
            
            ESTACIONES CON SEÑAL DEGRADADA (FL < 9.5 dB):
            {criticos}
            
            Detecta:
            1. ¿Hay estaciones con alto tráfico y baja señal? (Posible pérdida de paquetes).
            2. ¿Cuáles estaciones están en estado CRÍTICO (< 8dB)?
            3. Recomendación para el NOC.
            """
            
            with st.spinner("IA analizando patrones de tráfico y señal..."):
                reporte = get_gemini_analysis(prompt)
                st.session_state.last_report = reporte

        # Dashboard Visual
        tab_ia, tab_data, tab_charts = st.tabs(["🤖 Informe AI", "📋 Tabla de Datos", "📊 Gráficos"])
        
        with tab_ia:
            if 'last_report' in st.session_state:
                st.markdown(f"<div class='report-container'>{st.session_state.last_report}</div>", unsafe_allow_html=True)
            else:
                st.info("Haz clic en 'Iniciar Análisis Inteligente' para generar el reporte.")

        with tab_data:
            st.dataframe(data, use_container_width=True)

        with tab_charts:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.bar(data.head(10), x="Estación", y="Total_MB", title="Consumo Top 10 (MB)", color="Total_MB")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                if 'FL' in data.columns:
                    fig2 = px.scatter(data, x="Total_MB", y="FL", hover_name="Estación", 
                                     title="Correlación Tráfico vs Señal (FL)",
                                     labels={"FL": "Eb/No Forward Link (dB)"})
                    fig2.add_hline(y=9.0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("Por favor, cargue los tres archivos para realizar el análisis completo.")
