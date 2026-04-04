import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Meru Networks - Inteligencia Operacional",
    page_icon="📡",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .status-card {
        padding: 20px;
        border-radius: 12px;
        background-color: white;
        border: 1px solid #eef2f6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .ai-report {
        background-color: #f0f9ff;
        border-left: 6px solid #00aeef;
        padding: 25px;
        border-radius: 8px;
        color: #1e3a8a;
        line-height: 1.6;
    }
    .error-box {
        background-color: #fff1f2;
        border: 1px solid #fda4af;
        color: #9f1239;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGENCIA ARTIFICIAL ---
API_KEY = "" # El entorno inyecta la clave automáticamente

def get_ai_diagnosis(data_summary):
    """
    Consulta al modelo Gemini con manejo de errores avanzado y backoff exponencial.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    prompt = f"""
    Como Ingeniero Senior de Meru Networks, analiza estos datos de telemetría:
    {data_summary}
    
    Genera un informe técnico que incluya:
    1. Resumen de salud de la portadora.
    2. Identificación de anomalías (si las hay).
    3. Recomendación técnica inmediata.
    Responde en español, formato Markdown profesional.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                # Validación de la estructura de respuesta
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "⚠️ La IA no devolvió un diagnóstico válido. Estructura inesperada."
            
            elif response.status_code == 429:
                # Cuota excedida o Rate Limit
                time.sleep(2**i) # Backoff: 1s, 2s, 4s...
                continue
            else:
                return f"❌ Error de Servidor ({response.status_code}): {response.text[:100]}"
                
        except requests.exceptions.RequestException as e:
            if i == retries - 1:
                return f"📡 Error de conexión: No se pudo contactar al motor de IA. Verifique su acceso a internet. ({str(e)})"
            time.sleep(2**i)
            
    return "No se pudo obtener respuesta tras varios intentos."

# --- INTERFAZ ---
st.markdown("## 🛰️ Meru Networks - NOC Intelligence")
st.markdown("---")

# Layout Principal
col_dash, col_ai = st.columns([3, 2])

with col_dash:
    st.subheader("Panel de Telemetría")
    uploaded_file = st.file_uploader("Arrastre su archivo CSV de iDirect/Gilat aquí", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Intento de encontrar columnas numéricas relevantes
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        
        if not numeric_df.empty:
            target_col = numeric_df.columns[0]
            st.info(f"Visualizando columna: **{target_col}**")
            
            # Gráfico de Línea
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=df[target_col], mode='lines', line=dict(color='#3f4494')))
            fig.update_layout(title="Variación de Señal en el Tiempo", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            stats_text = f"Promedio: {df[target_col].mean():.2f}, Desviación: {df[target_col].std():.2f}, Puntos: {len(df)}"
        else:
            st.warning("No se encontraron datos numéricos en el archivo.")
            stats_text = "Sin datos válidos."

with col_ai:
    st.subheader("Diagnóstico Meru AI")
    if uploaded_file and not numeric_df.empty:
        if st.button("🚀 GENERAR INFORME INTELIGENTE"):
            with st.spinner("Conectando con Meru AI..."):
                diag = get_ai_diagnosis(stats_text)
                if "Error" in diag or "⚠️" in diag:
                    st.markdown(f'<div class="error-box">{diag}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-report">{diag}</div>', unsafe_allow_html=True)
    else:
        st.write("Cargue datos para habilitar el análisis de IA.")

# Footer Estático
st.divider()
st.caption("Terminal Operativa NOC v2.5 - Conectividad Satelital Avanzada")
