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
# El sistema inyecta la clave automáticamente en el entorno de ejecución
API_KEY = "" 
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Colores Corporativos Meru
MERU_BLUE = "#3f4494"
MERU_CYAN = "#00aeef"
MERU_DARK = "#0b0f19"

# --- FUNCIONES DE SOPORTE PARA IA ---

def call_gemini_api(prompt, system_prompt="Eres un experto en NOC y redes satelitales de Meru Networks."):
    """Llamada optimizada a Gemini con manejo de errores 403/429."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    
    # Reintentos con backoff exponencial
    for delay in [1, 2, 4, 8]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 403:
                return "⚠️ Error 403: Acceso denegado. Verificando permisos del modelo..."
            elif response.status_code == 429:
                time.sleep(delay)
            else:
                return f"⚠️ Error del sistema (Código: {response.status_code})"
        except Exception as e:
            return f"❌ Error de red: {str(e)}"
    
    return "No se pudo obtener respuesta de la IA tras varios intentos."

def analyze_visual_patterns(df, metric_name):
    """Genera una imagen de la métrica y la envía para análisis visual."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df[metric_name], color=MERU_CYAN, linewidth=1.5)
    ax.set_title(f"Patrón de Telemetría: {metric_name}", color="white")
    ax.grid(True, alpha=0.1)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    prompt = f"Analiza esta gráfica de {metric_name}. ¿Ves desvanecimiento por lluvia (rain fade), interferencia o saturación? Responde breve y técnico."
    
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
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error visual ({res.status_code})"
    except:
        return "Error al procesar la imagen con el cerebro de IA."

# --- INTERFAZ DE USUARIO (UI) ---

st.set_page_config(page_title="Meru Networks | Intel Hub", layout="wide", page_icon="📡")

# Estilos CSS
st.markdown(f"""
    <style>
    .stApp {{ background-color: {MERU_DARK}; color: white; }}
    .header-container {{ 
        display: flex; align-items: center; gap: 20px; 
        padding: 20px; background: rgba(255,255,255,0.03); 
        border-radius: 15px; border-left: 5px solid {MERU_CYAN};
        margin-bottom: 30px;
    }}
    .metric-box {{
        background: #161b22; border: 1px solid #30363d;
        padding: 25px; border-radius: 15px; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    .metric-label {{ color: {MERU_CYAN}; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
    .metric-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
    </style>
""", unsafe_allow_html=True)

# Logo de Meru en SVG para que no se pierda nunca
logo_html = f"""
<div class="header-container">
    <svg width="80" height="60" viewBox="0 0 100 60" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 50L45 10L60 35L75 15L95 50" stroke="{MERU_BLUE}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M30 50L50 25" stroke="{MERU_CYAN}" stroke-width="5" stroke-linecap="round"/>
        <path d="M65 50L80 35" stroke="{MERU_CYAN}" stroke-width="5" stroke-linecap="round"/>
    </svg>
    <div>
        <h1 style="margin:0; font-size: 28px; color: white; line-height: 1;">MERU <span style="color:{MERU_CYAN}">NETWORKS</span></h1>
        <p style="margin:5px 0 0 0; font-size: 11px; color: {MERU_CYAN}; letter-spacing: 4px; font-weight: 800;">SATELLITE INTELLIGENCE HUB</p>
    </div>
</div>
"""
st.markdown(logo_html, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Herramientas")
    file = st.file_uploader("Subir Reporte CSV", type="csv")
    if file:
        st.success("Reporte cargado correctamente.")

if file:
    # Carga de datos
    df = pd.read_csv(file)
    
    # Limpieza básica (quitar espacios en nombres de columnas)
    df.columns = [c.strip() for c in df.columns]
    
    # Identificar columnas numéricas para el selector
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if num_cols:
        col_select = st.selectbox("📊 Seleccionar Métrica de Telemetría", num_cols)
        
        # Dashboard Superior
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-box"><div class="metric-label">PROMEDIO</div><div class="metric-value">{df[col_select].mean():.2f}</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-box"><div class="metric-label">MÁXIMO</div><div class="metric-value">{df[col_select].max():.2f}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-box"><div class="metric-label">MUESTRAS</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
        
        # Gráfica Principal
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col_select],
            mode='lines',
            line=dict(color=MERU_CYAN, width=2),
            name=col_select,
            fill='tozeroy',
            fillcolor='rgba(0, 174, 239, 0.05)'
        ))
        fig.update_layout(
            template="plotly_dark", height=450,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # SECCIÓN IA
        st.markdown("---")
        st.subheader("🧠 Diagnóstico Asistido por IA")
        
        tab_chat, tab_vision = st.tabs(["💬 Consultar a la IA", "👁️ Escaneo Visual de Patrones"])
        
        with tab_chat:
            st.write("Hazle una pregunta a la IA sobre los logs:")
            pregunta = st.text_input("Ej: ¿A qué hora se detectó la mayor caída de señal?", key="chat_input")
            if st.button("Consultar Cerebro"):
                if pregunta:
                    with st.spinner("Analizando telemetría..."):
                        # Contexto enriquecido para la IA
                        data_summary = f"""
                        Métrica: {col_select}
                        Estadísticas: {df[col_select].describe().to_dict()}
                        Muestras: {len(df)}
                        Pregunta del usuario: {pregunta}
                        """
                        respuesta = call_gemini_api(data_summary)
                        st.info(respuesta)
                else:
                    st.warning("Escribe una consulta técnica.")
                    
        with tab_vision:
            st.write("La IA analizará la gráfica actual para detectar anomalías invisibles al ojo humano.")
            if st.button("Ejecutar Escaneo Visual"):
                with st.spinner("Escaneando formas de onda..."):
                    analisis_v = analyze_visual_patterns(df, col_select)
                    st.success(analisis_v)
    else:
        st.error("El archivo no contiene columnas numéricas procesables.")
else:
    st.info("💡 Sube un archivo CSV desde el panel lateral para iniciar el monitoreo inteligente.")
