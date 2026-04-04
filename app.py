import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
from io import StringIO

# Configuración de página
st.set_page_config(page_title="Meru VNO - AI Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .report-card { 
        background-color: #ffffff; 
        padding: 24px; 
        border-radius: 12px; 
        border-left: 6px solid #1a73e8; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        line-height: 1.6;
        color: #202124;
    }
    .ai-badge { 
        background-color: #e8f0fe; 
        color: #1967d2; 
        padding: 6px 14px; 
        border-radius: 8px; 
        font-weight: bold; 
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 10px;
    }
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Lógica de IA Gemini ---
apiKey = ""

def get_gemini_analysis(prompt_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres un experto en Redes Satelitales (NOC Tier 3). Tu objetivo es analizar logs y telemetría. Identifica saturación de tráfico, degradación de Eb/No (señal) y posibles fallas de hardware o clima. Sé profesional, técnico y ofrece soluciones accionables."}]
        }
    }
    
    # Reintentos con backoff exponencial
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=25)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(delay)
    return "No se pudo obtener el análisis de la IA. Por favor, verifica la conexión o reintenta en unos momentos."

# --- Procesamiento de Datos ---
def load_data(usage_file, stats_file):
    try:
        # 1. Procesar Tráfico (Usage Report)
        df_u = pd.read_csv(usage_file, skiprows=3)
        station_cols = [c for c in df_u.columns if c != 'Date']
        unique_stations = sorted(list(set([c.replace(' In', '').replace(' Out', '') for c in station_cols])))
        
        usage_summary = []
        for s in unique_stations:
            in_val = pd.to_numeric(df_u[f"{s} In"], errors='coerce').sum() if f"{s} In" in df_u.columns else 0
            out_val = pd.to_numeric(df_u[f"{s} Out"], errors='coerce').sum() if f"{s} Out" in df_u.columns else 0
            usage_summary.append({"Estación": s, "Download_MB": round(in_val, 2), "Upload_MB": round(out_val, 2), "Total_MB": round(in_val + out_val, 2)})
        
        df_usage = pd.DataFrame(usage_summary).sort_values("Total_MB", ascending=False)

        # 2. Procesar Eb/No (Statistics)
        df_s = pd.read_csv(stats_file)
        ebno_summary = []
        # Identificar columnas de Eb/No (RL y FL)
        ebno_cols = [c for c in df_s.columns if 'Eb/No' in c]
        
        for col in ebno_cols:
            parts = col.split('/')
            name = parts[0].strip().replace('"', '')
            tipo = "Return Link" if "RL" in col else "Forward Link"
            vals = pd.to_numeric(df_s[col], errors='coerce').dropna()
            if not vals.empty:
                ebno_summary.append({
                    "Estación": name, 
                    "Tipo": tipo, 
                    "EbNo_Min": round(vals.min(), 2),
                    "EbNo_Avg": round(vals.mean(), 2)
                })
        
        df_ebno = pd.DataFrame(ebno_summary)
        return df_usage, df_ebno
    except Exception as e:
        st.error(f"Error procesando archivos: {e}")
        return None, None

# --- UI Principal ---
st.title("🛰️ Meru Networks: AI Network Intelligence")
st.markdown("Diagnóstico avanzado de estaciones mediante Gemini 2.5 Flash.")

with st.sidebar:
    st.header("📂 Panel de Datos")
    u_file = st.file_uploader("Cargar Reporte de Tráfico (Usage)", type="csv")
    s_file = st.file_uploader("Cargar Estadísticas (Eb/No)", type="csv")
    st.divider()
    st.write("Sube los archivos descargados del NMS para iniciar el análisis automático.")

if u_file and s_file:
    df_usage, df_ebno = load_data(u_file, s_file)
    
    if df_usage is not None and df_ebno is not None:
        tab_ai, tab_stats = st.tabs(["🤖 Análisis de Gemini AI", "📊 Telemetría Detallada"])
        
        with tab_ai:
            st.markdown("<span class='ai-badge'>INTELIGENCIA ARTIFICIAL ACTIVA</span>", unsafe_allow_html=True)
            
            # Extraer estaciones críticas para el prompt
            criticas_ebno = df_ebno[df_ebno['EbNo_Avg'] < 9.0].sort_values("EbNo_Avg").head(5)
            top_trafico = df_usage.head(5)
            
            prompt = f"""
            Basado en los datos actuales del VNO:
            
            ESTACIONES CON SEÑAL BAJA (Eb/No < 9dB):
            {criticas_ebno.to_string(index=False)}
            
            ESTACIONES CON MAYOR CONSUMO (MB):
            {top_trafico.to_string(index=False)}
            
            Por favor, genera un informe que incluya:
            1. Diagnóstico de las 3 estaciones con mayor riesgo de caída.
            2. Análisis de si el consumo alto está afectando la señal (saturación).
            3. Recomendaciones técnicas (ej: revisión de BUC/LNB, cambio de MODCOD o repunteo).
            Responde en español de forma ejecutiva.
            """
            
            if 'report_text' not in st.session_state:
                with st.spinner("Gemini está analizando las tendencias de la red..."):
                    st.session_state.report_text = get_gemini_analysis(prompt)
            
            st.markdown(f"<div class='report-card'>{st.session_state.report_text}</div>", unsafe_allow_html=True)
            
            if st.button("🔄 Generar Nuevo Análisis"):
                del st.session_state.report_text
                st.rerun()

        with tab_stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribución de Tráfico (MB)")
                fig_u = px.pie(df_usage.head(10), values='Total_MB', names='Estación', 
                               hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_u, use_container_width=True)
            
            with col2:
                st.subheader("Niveles Eb/No por Estación")
                fig_e = px.bar(df_ebno.sort_values("EbNo_Avg"), x="EbNo_Avg", y="Estación", 
                               color="EbNo_Avg", orientation='h',
                               color_continuous_scale="RdYlGn",
                               range_color=[7, 15],
                               labels={'EbNo_Avg': 'Eb/No Promedio (dB)'})
                st.plotly_chart(fig_e, use_container_width=True)
            
            st.divider()
            st.subheader("Tabla Maestra de Estaciones")
            st.dataframe(df_usage, use_container_width=True)
else:
    st.info("👋 Bienvenida/o. Por favor, carga los archivos CSV en el panel lateral para comenzar el análisis.")
    
    # Placeholder de visualización
    col_x, col_y = st.columns(2)
    with col_x:
        st.image("https://img.icons8.com/clouds/200/satellite.png")
    with col_y:
        st.markdown("""
        ### Instrucciones de uso:
        1. Sube el archivo **Usage Report** (Tráfico).
        2. Sube el archivo **Statistics** (Eb/No).
        3. El sistema procesará automáticamente los datos.
        4. Gemini generará un diagnóstico técnico de salud de red.
        """)
