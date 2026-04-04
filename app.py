import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import base64
import time
import io

# --- CONFIGURACIÓN DE LA PLATAFORMA ---
API_KEY = ""  # El entorno inyecta la clave automáticamente
MODEL_TEXT = "gemini-2.5-flash-preview-09-2025"
MODEL_IMAGE = "gemini-2.5-flash-preview-09-2025"

# --- FUNCIONES DE ANÁLISIS ---

def detect_anomalies(data):
    """Detecta anomalías estadísticas usando Z-Score."""
    mean = np.mean(data)
    std = np.std(data)
    if std < 0.001: return []
    z_scores = [(y - mean) / std for y in data]
    return np.where(np.abs(z_scores) > 2.2)[0]

def analyze_with_ai(df, metric_name, prompt_custom=None):
    """Genera un análisis de texto basado en los datos estadísticos."""
    resumen = df[metric_name].describe().to_json()
    ultimos = df[metric_name].tail(10).to_string()
    
    contexto = f"""
    Métrica analizada: {metric_name}
    Estadísticas: {resumen}
    Últimos valores: {ultimos}
    Pregunta: {prompt_custom if prompt_custom else "Realiza un diagnóstico técnico."}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_TEXT}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": contexto}]}],
        "systemInstruction": {"parts": [{"text": "Eres el experto en redes de Meru NOC. Analiza los datos y da soluciones técnicas."}]}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=20)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Error consultando al cerebro de IA."

def analyze_visual_patterns(df, metric_name):
    """Crea una imagen del gráfico y la envía a la IA para análisis de visión."""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df.index, df[metric_name], color='#00d4ff', linewidth=2)
    ax.set_title(f"Visual Pattern Scan: {metric_name}")
    ax.grid(True, alpha=0.1)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_IMAGE}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Analiza visualmente esta gráfica de red. ¿Ves comportamientos sospechosos como ataques DDoS, jitter excesivo o caídas periódicas? Responde técnico en español."},
                {"inlineData": {"mimeType": "image/png", "data": img_base64}}
            ]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=25)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "El motor de visión no pudo procesar la imagen actual."

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Meru NOC AI", layout="wide", page_icon="📡")

st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .ai-box { background-color: #051525; border-left: 4px solid #58a6ff; padding: 20px; border-radius: 8px; color: #adbac7; }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Meru NOC Intelligence Center")
st.caption("Importación de CSV + Diagnóstico Híbrido por IA")

# Sidebar
with st.sidebar:
    st.header("Entrada de Datos")
    file = st.file_uploader("Cargar CSV de Red", type="csv")
    if file:
        st.success("Archivo listo para procesar")

if file:
    df = pd.read_csv(file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.error("No hay datos numéricos en el archivo.")
    else:
        # Dashboard Principal
        col1, col2, col3 = st.columns(3)
        selected_metric = st.selectbox("Seleccione Métrica para Monitoreo", numeric_cols)
        
        idx_anom = detect_anomalies(df[selected_metric])
        
        col1.metric("Valor Actual", f"{df[selected_metric].iloc[-1]:.2f}")
        col2.metric("Promedio de Sesión", f"{df[selected_metric].mean():.2f}")
        col3.metric("Anomalías Detectadas", len(idx_anom), delta_color="inverse" if len(idx_anom) > 0 else "normal")

        # Gráfico con Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[selected_metric], name="Flujo de Red", line=dict(color='#58a6ff', width=2)))
        
        if len(idx_anom) > 0:
            fig.add_trace(go.Scatter(x=idx_anom, y=df[selected_metric].iloc[idx_anom], mode='markers', 
                                    marker=dict(color='#f85149', size=8), name="Anomalía Critica"))
        
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Zona de Inteligencia Artificial
        st.divider()
        st.subheader("🤖 Diagnóstico Asistido por IA")
        
        tab1, tab2 = st.tabs(["💬 Consultar a la IA", "👁️ Escaneo Visual de Patrones"])
        
        with tab1:
            q = st.text_input("Hazle una pregunta a la IA sobre los logs:", placeholder="¿Qué causó el pico de tráfico observado?")
            if st.button("Ejecutar Análisis de Texto"):
                with st.spinner("Procesando telemetría..."):
                    ans = analyze_with_ai(df, selected_metric, q)
                    st.markdown(f'<div class="ai-box">{ans}</div>', unsafe_allow_html=True)
        
        with tab2:
            st.info("La IA analizará la forma del gráfico para detectar comportamientos no lineales.")
            if st.button("Iniciar Visión Artificial"):
                with st.spinner("Escaneando formas de onda..."):
                    ans_v = analyze_visual_patterns(df, selected_metric)
                    st.markdown(f'<div class="ai-box"><b>Análisis Visual de IA:</b><br><br>{ans_v}</div>', unsafe_allow_html=True)

else:
    # Pantalla de espera
    st.info("Esperando carga de archivo CSV para inicializar el NOC...")
    st.image("https://img.icons8.com/fluency/200/combo-chart.png", width=120)
    if st.button("Generar CSV de prueba para Meru"):
        t = np.linspace(0, 24, 100)
        y = 50 + 10*np.sin(t) + np.random.normal(0, 2, 100)
        y[50:55] = y[50:55] * 3 # Simular pico de ataque
        test_df = pd.DataFrame({'Hora': t, 'Latencia_ms': y, 'Trafico_Mbps': y*0.8})
        st.download_button("Descargar CSV de Prueba", test_df.to_csv(index=False), "log_red_meru.csv")
