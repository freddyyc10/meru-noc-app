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
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .ai-badge { background-color: #e3f2fd; color: #0d47a1; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_stdio=True)

# --- Lógica de IA Gemini ---
apiKey = ""

def get_gemini_analysis(prompt_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres un Ingeniero de Soporte Nivel 3 en Redes Satelitales. Tu tarea es analizar logs de tráfico y niveles de Eb/No. Identifica degradación de servicio, posibles fallas de hardware, o problemas de clima. Sé conciso, técnico y directo."}]
        }
    }
    
    for delay in [1, 2, 4]: # Reintentos rápidos
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            time.sleep(delay)
    return "⚠️ El servicio de análisis de IA no pudo responder en este momento. Intente nuevamente."

# --- Procesamiento de Datos ---
def load_data(usage_file, stats_file):
    try:
        # 1. Procesar Tráfico (Usage)
        # Saltamos las primeras 3 filas como en el archivo original
        df_u = pd.read_csv(usage_file, skiprows=3)
        station_cols = [c for c in df_u.columns if c != 'Date']
        unique_stations = sorted(list(set([c.replace(' In', '').replace(' Out', '') for c in station_cols])))
        
        usage_summary = []
        for s in unique_stations:
            in_val = pd.to_numeric(df_u[f"{s} In"], errors='coerce').sum() if f"{s} In" in df_u.columns else 0
            out_val = pd.to_numeric(df_u[f"{s} Out"], errors='coerce').sum() if f"{s} Out" in df_u.columns else 0
            usage_summary.append({"Estación": s, "Download_MB": in_val, "Upload_MB": out_val, "Total_MB": in_val + out_val})
        
        df_usage = pd.DataFrame(usage_summary).sort_values("Total_MB", ascending=False)

        # 2. Procesar Eb/No (Statistics)
        df_s = pd.read_csv(stats_file)
        ebno_summary = []
        ebno_cols = [c for c in df_s.columns if 'Eb/No' in c]
        
        for col in ebno_cols:
            name = col.split('/')[0].strip()
            tipo = "RL (Return)" if "RL" in col else "FL (Forward)"
            mean_val = pd.to_numeric(df_s[col], errors='coerce').mean()
            if not np.isnan(mean_val):
                ebno_summary.append({"Estación": name, "Tipo": tipo, "EbNo_Avg": round(mean_val, 2)})
        
        df_ebno = pd.DataFrame(ebno_summary)
        return df_usage, df_ebno
    except Exception as e:
        st.error(f"Error en estructura de archivos: {e}")
        return None, None

# --- Interfaz de Usuario ---
st.title("🛰️ Meru Networks AI Insights")
st.markdown("Analizador de rendimiento de estaciones VNO mediante Inteligencia Artificial.")

with st.sidebar:
    st.header("Carga de Datos")
    u_file = st.file_uploader("CSV de Tráfico (Usage Report)", type="csv")
    s_file = st.file_uploader("CSV de Eb/No (Statistics)", type="csv")
    st.info("Sube ambos archivos para iniciar el diagnóstico automático.")

if u_file and s_file:
    df_usage, df_ebno = load_data(u_file, s_file)
    
    if df_usage is not None and df_ebno is not None:
        # Layout de la Aplicación
        tab1, tab2 = st.tabs(["🤖 Diagnóstico IA", "📊 Métricas de Red"])
        
        with tab1:
            st.markdown("### <span class='ai-badge'>GEMINI 2.5 FLASH</span> Análisis de Salud de Red", unsafe_allow_stdio=True)
            
            # Preparar contexto para la IA
            top_usage = df_usage.head(8).to_string(index=False)
            worst_ebno = df_ebno.sort_values("EbNo_Avg").head(8).to_string(index=False)
            
            prompt = f"""
            Analiza los siguientes datos de la red Meru VNO:
            
            TOP CONSUMO (MB):
            {top_usage}
            
            PEORES NIVELES Eb/No (dB):
            {worst_ebno}
            
            1. ¿Existen estaciones con alto tráfico pero señal marginal (Eb/No < 8dB)?
            2. Identifica si alguna estación parece tener problemas de apuntamiento (Eb/No bajo constante).
            3. Da 3 recomendaciones técnicas de prioridad inmediata.
            """
            
            with st.container():
                st.markdown("<div class='report-card'>", unsafe_allow_stdio=True)
                if 'ai_report' not in st.session_state:
                    with st.spinner("Gemini está analizando los patrones de red..."):
                        st.session_state.ai_report = get_gemini_analysis(prompt)
                
                st.markdown(st.session_state.ai_report)
                st.markdown("</div>", unsafe_allow_stdio=True)
                
                if st.button("🔄 Recalcular Análisis"):
                    del st.session_state.ai_report
                    st.rerun()

        with tab2:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Tráfico por Estación")
                fig_u = px.bar(df_usage.head(15), x="Total_MB", y="Estación", orientation='h', 
                               color="Total_MB", color_continuous_scale="Viridis")
                st.plotly_chart(fig_u, use_container_width=True)
                
            with col2:
                st.subheader("Calidad de Señal (Eb/No)")
                fig_e = px.scatter(df_ebno, x="Estación", y="EbNo_Avg", color="Tipo", 
                                   title="Eb/No Promedio por Estación", height=400)
                st.plotly_chart(fig_e, use_container_width=True)
            
            st.subheader("Datos Crudos Procesados")
            st.dataframe(df_usage, use_container_width=True)

else:
    # Pantalla de espera interactiva
    st.empty()
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        st.image("https://img.icons8.com/fluency/96/satellite-sending-signal.png", width=100)
        st.warning("Esperando archivos CSV para iniciar el análisis...")
        st.write("Por favor, carga los reportes en el panel lateral izquierdo.")
