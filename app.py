import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import base64
import time
import io

# --- CONFIGURACIÓN DE IDENTIDAD Y API ---
API_KEY = ""  # El sistema inyecta la clave automáticamente
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Colores Corporativos Meru
MERU_BLUE = "#3f4494"
MERU_CYAN = "#00aeef"
MERU_DARK = "#0b0f19"

# --- FUNCIONES DE SOPORTE ---

def call_gemini(prompt, system_prompt="Eres un experto en redes satelitales de Meru Networks."):
    """Llamada directa a Gemini con reintentos."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    
    for delay in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                time.sleep(delay)
            else:
                return f"⚠️ Error del servidor (Código: {response.status_code})"
        except Exception as e:
            return f"❌ Error de conexión: {str(e)}"
    return "No se pudo conectar con Gemini tras varios intentos."

def get_visual_analysis(df, metric):
    """Genera una imagen y la analiza con la visión de Gemini."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df[metric], color=MERU_CYAN, linewidth=1.5)
    ax.set_title(f"Análisis de Patrones: {metric}", color="white")
    ax.grid(True, alpha=0.1)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    prompt = f"Analiza esta gráfica de la métrica {metric}. Busca anomalías, picos de congestión o degradación de señal satelital. Responde en español técnico."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/png", "data": img_b64}}
            ]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "El motor visual no pudo procesar la imagen."

# --- INTERFAZ DE USUARIO ---

st.set_page_config(page_title="Meru Networks | Intel Hub", layout="wide", page_icon="📡")

# Estilo y Logo
st.markdown(f"""
    <style>
    .stApp {{ background-color: {MERU_DARK}; color: white; }}
    .header-box {{ 
        display: flex; align-items: center; gap: 20px; 
        padding: 20px; background: rgba(255,255,255,0.05); 
        border-radius: 15px; border-left: 5px solid {MERU_CYAN};
        margin-bottom: 25px;
    }}
    .metric-card {{
        background: #161b22; border: 1px solid #30363d;
        padding: 20px; border-radius: 12px; text-align: center;
    }}
    </style>
""", unsafe_allow_html=True)

# Logo SVG de Meru
logo_svg = f"""
<div class="header-box">
    <svg width="80" height="50" viewBox="0 0 100 60" fill="none">
        <path d="M10 50L40 10L55 35L70 15L90 50" stroke="{MERU_BLUE}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M25 50L45 25" stroke="{MERU_CYAN}" stroke-width="4" stroke-linecap="round"/>
        <path d="M60 50L75 35" stroke="{MERU_CYAN}" stroke-width="4" stroke-linecap="round"/>
    </svg>
    <div>
        <h1 style="margin:0; font-size: 24px; letter-spacing:-1px;">
            <span style="color:{MERU_CYAN}">MERU</span> <span style="color:white">NETWORKS</span>
        </h1>
        <p style="margin:0; font-size:10px; color:{MERU_CYAN}; letter-spacing: 3px; font-weight:bold;">SATELLITE INTELLIGENCE HUB</p>
    </div>
</div>
"""
st.markdown(logo_svg, unsafe_allow_html=True)

# Sidebar para carga de archivos
with st.sidebar:
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Cargar Reporte (CSV)", type="csv")
    if uploaded_file:
        st.success("Archivo cargado con éxito")

if uploaded_file:
    # Procesamiento flexible del CSV
    df = pd.read_csv(uploaded_file)
    
    # Identificar columnas numéricas automáticamente
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not num_cols:
        st.error("No se detectaron columnas numéricas en este archivo. Verifique el formato.")
    else:
        # Selección de métrica
        metric = st.selectbox("Seleccionar Métrica de Telemetría", num_cols)
        
        # Dashboard de métricas rápidas
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><small>PROMEDIO</small><h3>{df[metric].mean():.2f}</h3></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><small>MÁXIMO</small><h3>{df[metric].max():.2f}</h3></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><small>MUESTRAS</small><h3>{len(df)}</h3></div>', unsafe_allow_html=True)
        
        st.write("")
        
        # Gráfico Interactivo
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df[metric], 
            line=dict(color=MERU_CYAN, width=2),
            fill='tozeroy', fillcolor='rgba(0, 174, 239, 0.1)'
        ))
        fig.update_layout(
            template="plotly_dark", height=400, 
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # SECCIÓN DE IA
        st.markdown("---")
        st.subheader("🤖 Diagnóstico Asistido por Gemini")
        
        t1, t2 = st.tabs(["💬 Consultar Telemetría", "👁️ Análisis Visual de IA"])
        
        with t1:
            user_q = st.text_input("Pregunta algo sobre estos datos:", placeholder="Ej: ¿Hay indicios de lluvia en la señal?")
            if st.button("Analizar con Gemini"):
                if user_q:
                    with st.spinner("Gemini analizando datos..."):
                        # Pasar un resumen de los datos para contexto
                        context = f"Métrica: {metric}. Resumen: {df[metric].describe().to_string()}. Pregunta: {user_q}"
                        response = call_gemini(context)
                        st.info(response)
                else:
                    st.warning("Por favor escribe una pregunta.")
                    
        with t2:
            st.write("Gemini analizará la 'forma' de la gráfica para encontrar patrones de congestión.")
            if st.button("Escanear Patrones Gráficos"):
                with st.spinner("Procesando imagen técnica..."):
                    v_response = get_visual_analysis(df, metric)
                    st.success(v_response)

else:
    # Pantalla inicial
    st.info("👋 Bienvenido al Centro de Inteligencia de Meru Networks. Por favor, sube un archivo CSV para iniciar el análisis.")
    
    st.markdown("### Generar datos de prueba")
    if st.button("Crear CSV de Simulación"):
        t = np.arange(0, 50)
        # Simular señal satelital con una caída (lluvia) y ruido
        signal = 12 + np.random.normal(0, 0.5, 50)
        signal[20:30] = signal[20:30] - 5 # Degradación
        test_df = pd.DataFrame({'Minuto': t, 'EbNo_dB': signal, 'Traffic_kbps': signal * 100})
        st.download_button("Descargar CSV de Prueba", test_df.to_csv(index=False), "test_meru.csv")
