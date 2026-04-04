import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
import io

# Configuración de página
st.set_page_config(page_title="Meru VNO - AI Network Insights", layout="wide")

# --- Estilos CSS (Sin dependencias externas) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .report-container { 
        background-color: white; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 8px solid #007bff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        color: #2c3e50;
        line-height: 1.6;
    }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- Configuración de API Gemini (Inyectada automáticamente) ---
apiKey = "" 

def get_gemini_analysis(prompt_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres un experto en NOC de redes satelitales. Tu tarea es analizar el tráfico y los niveles Eb/No. Identifica estaciones con señal crítica (FL < 9dB) y alto consumo. Ofrece recomendaciones técnicas en español."}]
        }
    }
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=25)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except: time.sleep(delay)
    return "La IA no pudo procesar el reporte en este momento. Por favor reintente."

# --- Procesador de Datos Robusto ---
def process_data(usage_file, stats_file):
    try:
        # 1. Procesar Tráfico (Usage Report) - Saltando las 3 líneas de Meru
        u_bytes = usage_file.getvalue().decode('utf-8')
        df_u_raw = pd.read_csv(io.StringIO(u_bytes), skiprows=3)
        
        usage_list = []
        for col in df_u_raw.columns:
            if col.endswith(" In"):
                st_name = col.replace(" In", "").strip()
                in_val = pd.to_numeric(df_u_raw[col], errors='coerce').sum()
                out_col = f"{st_name} Out"
                out_val = pd.to_numeric(df_u_raw[out_col], errors='coerce').sum() if out_col in df_u_raw.columns else 0
                usage_list.append({"Estación": st_name, "MB_Total": round(in_val + out_val, 2)})
        df_usage = pd.DataFrame(usage_list)

        # 2. Procesar Eb/No (Statistics 44/45)
        s_bytes = stats_file.getvalue().decode('utf-8')
        df_s_raw = pd.read_csv(io.StringIO(s_bytes))
        
        ebno_list = []
        for col in df_s_raw.columns:
            if "/" in col and "Eb/No" in col:
                st_name = col.split("/")[0].replace('"', '').strip()
                link_type = "FL" if "FL" in col else "RL"
                avg_val = pd.to_numeric(df_s_raw[col], errors='coerce').mean()
                if not np.isnan(avg_val):
                    ebno_list.append({"Estación": st_name, "Tipo": link_type, "Val": round(avg_val, 2)})
        
        if ebno_list:
            df_ebno = pd.DataFrame(ebno_list).pivot_table(index="Estación", columns="Tipo", values="Val").reset_index()
            # Unir datos
            return pd.merge(df_usage, df_ebno, on="Estación", how="inner")
        return None
    except Exception as e:
        st.error(f"Error al procesar archivos: {e}")
        return None

# --- UI ---
st.title("🛰️ Meru VNO AI Diagnostics")

with st.sidebar:
    st.header("Archivos del HUB")
    u_f = st.file_uploader("Subir Usage Report (20)", type="csv")
    s_f = st.file_uploader("Subir Statistics (44 o 45)", type="csv")
    st.divider()
    btn = st.button("🪄 Generar Análisis IA", type="primary", use_container_width=True)

if u_f and s_f:
    df = process_data(u_f, s_f)
    
    if df is not None:
        # Métricas principales
        c1, c2, c3 = st.columns(3)
        c1.metric("Estaciones Reportadas", len(df))
        c2.metric("Tráfico Total (GB)", f"{df['MB_Total'].sum()/1024:.1f}")
        if 'FL' in df.columns:
            c3.metric("Eb/No FL Promedio", f"{df['FL'].mean():.1f} dB")

        t1, t2 = st.tabs(["🤖 Informe de Gemini", "📊 Telemetría y Gráficos"])

        with t1:
            if btn:
                with st.spinner("Analizando con Gemini 2.5 Flash..."):
                    # Enviamos solo lo relevante para no saturar el prompt
                    top_ia = df.sort_values("FL").head(10).to_string(index=False)
                    res = get_gemini_analysis(f"Analiza estas estaciones (las de menor Eb/No):\n{top_ia}")
                    st.markdown(f"<div class='report-container'>{res}</div>", unsafe_allow_html=True)
            else:
                st.info("Presiona el botón en la barra lateral para iniciar el análisis con IA.")

        with t2:
            st.subheader("Estado de Estaciones")
            st.dataframe(df.sort_values("MB_Total", ascending=False), use_container_width=True)
            
            if 'FL' in df.columns:
                fig = px.scatter(df, x="MB_Total", y="FL", hover_name="Estación", 
                                 title="Correlación: Consumo vs Calidad de Señal",
                                 labels={"FL": "Eb/No Forward (dB)", "MB_Total": "Tráfico (MB)"})
                fig.add_hline(y=9.0, line_dash="dash", line_color="red")
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Por favor, carga los archivos CSV en el panel lateral.")
