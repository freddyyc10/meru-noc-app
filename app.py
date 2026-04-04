import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
import io

# Configuración de página
st.set_page_config(page_title="Meru VNO AI Analytics", layout="wide")

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .report-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #1E88E5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        background: #f1f3f4;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Lógica de IA (Gemini) ---
apiKey = ""

def get_ai_analysis(data_summary):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    prompt = f"""
    Como experto en NOC Satelital, analiza el siguiente resumen de tráfico y niveles Eb/No de un VNO iDirect.
    Identifica:
    1. Estaciones con FL Eb/No por debajo de 9.5 dB (Posible apuntamiento o clima).
    2. Estaciones con alto consumo pero baja señal.
    3. Recomendaciones de mantenimiento preventivo.
    
    Datos:
    {data_summary}
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "Responde de forma técnica pero concisa en español."}]}
    }
    
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except: time.sleep(delay)
    return "Error al conectar con la IA. Verifique su conexión."

# --- Procesador de Archivos Específicos ---
def process_meru_files(usage_file, stats_file):
    try:
        # 1. Procesar Reporte de Uso (Saltar encabezado de Meru)
        u_content = usage_file.getvalue().decode('utf-8')
        df_u_raw = pd.read_csv(io.StringIO(u_content), skiprows=3)
        
        usage_data = []
        # Agrupar In/Out por estación
        cols = [c for c in df_u_raw.columns if " In" in c or " Out" in c]
        for col in cols:
            st_name = col.replace(" In", "").replace(" Out", "").strip()
            val = pd.to_numeric(df_u_raw[col], errors='coerce').sum()
            usage_data.append({"Estación": st_name, "Valor": val})
        
        df_usage = pd.DataFrame(usage_data).groupby("Estación")["Valor"].sum().reset_index()
        df_usage.columns = ["Estación", "MB_Total"]

        # 2. Procesar Estadísticas Eb/No (Report 44)
        s_content = stats_file.getvalue().decode('utf-8')
        df_s_raw = pd.read_csv(io.StringIO(s_content))
        
        ebno_data = []
        for col in df_s_raw.columns:
            if "/" in col:
                parts = col.split("/")
                st_name = parts[0].replace('"', '').strip()
                tipo = "FL" if "FL" in parts[1] else "RL"
                avg_val = pd.to_numeric(df_s_raw[col], errors='coerce').mean()
                if not np.isnan(avg_val):
                    ebno_data.append({"Estación": st_name, "Tipo": tipo, "Val": avg_val})
        
        if ebno_data:
            df_ebno = pd.DataFrame(ebno_data).pivot_table(index="Estación", columns="Tipo", values="Val").reset_index()
            # Unir con consumo
            final_df = pd.merge(df_usage, df_ebno, on="Estación", how="inner")
            return final_df
        return None
    except Exception as e:
        st.error(f"Error técnico al procesar: {e}")
        return None

# --- Interfaz de Usuario ---
st.title("📊 Meru NOC - AI Assistant")
st.markdown("Analice reportes de **Uso** y **Estadísticas (44)** para diagnosticar el estado del VNO.")

with st.sidebar:
    st.header("Carga de Datos")
    f_usage = st.file_uploader("Usage Report (CSV)", type="csv")
    f_stats = st.file_uploader("Statistics 44 (CSV)", type="csv")
    st.divider()
    analyze_btn = st.button("🚀 Ejecutar Análisis IA", type="primary", use_container_width=True)

if f_usage and f_stats:
    df = process_meru_files(f_usage, f_stats)
    
    if df is not None:
        # Layout de métricas
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Estaciones Activas", len(df))
        with m2: st.metric("Consumo Total", f"{df['MB_Total'].sum()/1024:.2f} GB")
        with m3: 
            if 'FL' in df.columns:
                st.metric("Eb/No FL Avg", f"{df['FL'].mean():.2f} dB")

        tab_ia, tab_data, tab_viz = st.tabs(["🤖 Diagnóstico IA", "📋 Datos Crudos", "📈 Gráficos"])

        with tab_ia:
            if analyze_btn:
                with st.spinner("Gemini analizando patrones de red..."):
                    # Enviamos estaciones críticas a la IA
                    criticas = df.sort_values("FL").head(15).to_string(index=False)
                    analisis = get_ai_analysis(criticas)
                    st.markdown(f"<div class='report-card'>{analisis}</div>", unsafe_allow_html=True)
            else:
                st.info("Haz clic en 'Ejecutar Análisis IA' para recibir el reporte técnico.")

        with tab_data:
            st.subheader("Reporte Consolidado")
            # Mostrar tabla ordenada por mayor consumo
            st.dataframe(df.sort_values("MB_Total", ascending=False), use_container_width=True)

        with tab_viz:
            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.bar(df.sort_values("MB_Total", ascending=False).head(10), 
                             x="Estación", y="MB_Total", title="Top 10 Consumo (MB)")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_b:
                if 'FL' in df.columns:
                    fig2 = px.scatter(df, x="MB_Total", y="FL", hover_name="Estación", 
                                     title="Salud de Señal vs Consumo",
                                     labels={"FL": "Eb/No Forward", "MB_Total": "MB"})
                    fig2.add_hline(y=9.5, line_dash="dash", line_color="red", annotation_text="Umbral Crítico")
                    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("⚠️ Esperando carga de archivos CSV en la barra lateral.")
