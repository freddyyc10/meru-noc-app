import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
import io

# Configuración de página
st.set_page_config(page_title="Meru VNO - Inteligencia de Red", layout="wide")

# --- Estilos CSS ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .report-container { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 8px solid #1E88E5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .status-critical { color: #d32f2f; font-weight: bold; }
    .status-ok { color: #388e3c; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Configuración de API Gemini (Gestión Automática) ---
apiKey = "" 

def get_gemini_analysis(prompt_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "systemInstruction": {
            "parts": [{"text": "Eres un experto en telemetría satelital y NOC. Analiza tablas de consumo (MB) y niveles Eb/No. Identifica estaciones con bajo Eb/No (menor a 9dB) y alto tráfico. Genera un diagnóstico técnico y recomendaciones de re-apuntamiento o revisión de hardware."}]
        }
    }
    # Implementación de reintentos con backoff exponencial
    for delay in [1, 2, 4, 8]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            time.sleep(delay)
    return "No se pudo obtener el diagnóstico de la IA tras varios intentos. Verifique la conexión."

# --- Procesamiento de Archivos ---
def process_vno_data(usage_file, ebno_file):
    try:
        # 1. Procesar Reporte de Uso (Uso de MB)
        # Saltamos 3 líneas como indica la estructura del archivo
        usage_bytes = usage_file.getvalue().decode('utf-8')
        df_usage_raw = pd.read_csv(io.StringIO(usage_bytes), skiprows=3)
        
        usage_data = []
        # Buscamos columnas que terminen en " In"
        for col in df_usage_raw.columns:
            if col.endswith(" In"):
                station_name = col.replace(" In", "").strip()
                out_col = f"{station_name} Out"
                
                in_val = pd.to_numeric(df_usage_raw[col], errors='coerce').sum()
                out_val = pd.to_numeric(df_usage_raw[out_col], errors='coerce').sum() if out_col in df_usage_raw.columns else 0
                
                usage_data.append({
                    "Estación": station_name,
                    "In_MB": in_val,
                    "Out_MB": out_val,
                    "Total_MB": in_val + out_val
                })
        
        df_usage = pd.DataFrame(usage_data)

        # 2. Procesar Statistics (Eb/No)
        ebno_bytes = ebno_file.getvalue().decode('utf-8')
        df_ebno_raw = pd.read_csv(io.StringIO(ebno_bytes))
        
        ebno_stats = []
        for col in df_ebno_raw.columns:
            if "/" in col and "Eb/No" in col:
                # El formato es "NOMBRE_ESTACION/TIPO Eb/No"
                parts = col.split("/")
                station_name = parts[0].replace('"', '').strip()
                metric_name = parts[1]
                
                avg_val = pd.to_numeric(df_ebno_raw[col], errors='coerce').mean()
                
                # Identificar si es Forward Link o Return Link
                link_type = "FL" if "FL" in metric_name else "RL"
                
                ebno_stats.append({
                    "Estación": station_name,
                    "Tipo": link_type,
                    "Valor": avg_val
                })
        
        df_ebno_long = pd.DataFrame(ebno_stats)
        # Pivotamos para tener FL y RL en columnas separadas
        df_ebno_pivot = df_ebno_long.pivot_table(index="Estación", columns="Tipo", values="Valor").reset_index()

        # 3. Cruzar los datos (Merge)
        df_final = pd.merge(df_usage, df_ebno_pivot, on="Estación", how="inner")
        return df_final

    except Exception as e:
        st.error(f"Error en el procesamiento: {e}")
        return None

# --- UI de la Aplicación ---
st.title("🛰️ Analizador de Telemetría Meru VNO")
st.markdown("Cruce de datos de consumo y niveles de señal para diagnóstico automático.")

with st.sidebar:
    st.header("Carga de Archivos")
    u_file = st.file_uploader("Subir Usage Report (.csv)", type="csv")
    e_file = st.file_uploader("Subir Statistics Eb/No (.csv)", type="csv")
    
    analyze_btn = st.button("Analizar con IA", type="primary", use_container_width=True)

if u_file and e_file:
    with st.spinner("Procesando datos..."):
        full_df = process_vno_data(u_file, e_file)

    if full_df is not None:
        # Métricas Generales
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Estaciones", len(full_df))
        m2.metric("Consumo Total (GB)", f"{full_df['Total_MB'].sum()/1024:.2f}")
        
        avg_fl = full_df['FL'].mean() if 'FL' in full_df.columns else 0
        m3.metric("Promedio Eb/No FL", f"{avg_fl:.2f} dB")

        # Tabs para visualización
        tab1, tab2, tab3 = st.tabs(["📊 Visualización", "📋 Datos Crudos", "🤖 Diagnóstico IA"])

        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                fig_cons = px.bar(full_df.sort_values("Total_MB", ascending=False).head(15), 
                                 x="Estación", y="Total_MB", title="Top 15 Consumo (MB)",
                                 color_discrete_sequence=['#1E88E5'])
                st.plotly_chart(fig_cons, use_container_width=True)
            
            with col_b:
                if 'FL' in full_df.columns:
                    fig_signal = px.scatter(full_df, x="Total_MB", y="FL", 
                                          hover_name="Estación", title="Tráfico vs Calidad de Señal (FL)",
                                          labels={"FL": "Eb/No Forward (dB)", "Total_MB": "Tráfico Total (MB)"})
                    fig_signal.add_hline(y=9.0, line_dash="dash", line_color="red", annotation_text="Umbral Crítico")
                    st.plotly_chart(fig_signal, use_container_width=True)

        with tab2:
            st.dataframe(full_df.style.background_gradient(subset=['FL'], cmap='RdYlGn', vmin=7, vmax=12), use_container_width=True)

        with tab3:
            if analyze_btn:
                # Filtrar casos interesantes para la IA (bajo nivel de señal o alto tráfico)
                criticos = full_df[full_df['FL'] < 9.5].sort_values('FL')
                tops = full_df.sort_values('Total_MB', ascending=False).head(10)
                
                contexto = f"""
                DATOS DE ESTACIONES CRÍTICAS (Señal < 9.5dB):
                {criticos[['Estación', 'Total_MB', 'FL', 'RL']].to_string() if 'RL' in full_df.columns else criticos[['Estación', 'Total_MB', 'FL']].to_string()}
                
                DATOS DE MAYOR CONSUMO:
                {tops[['Estación', 'Total_MB', 'FL']].to_string()}
                """
                
                with st.spinner("Gemini analizando patrones..."):
                    diagnostico = get_gemini_analysis(contexto)
                    st.markdown(f"<div class='report-container'>{diagnostico}</div>", unsafe_allow_html=True)
            else:
                st.info("Presiona el botón 'Analizar con IA' en el panel lateral para obtener el diagnóstico detallado.")
else:
    st.info("👋 Por favor, carga los archivos .csv para comenzar.")
