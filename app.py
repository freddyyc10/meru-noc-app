import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE API IA ---
# El entorno proporciona la clave automáticamente
apiKey = ""

def call_gemini_analysis(data_summary):
    """Llamada a Gemini 2.5 Flash para análisis de red con Backoff Exponencial"""
    system_prompt = "Eres el Ingeniero Senior de Meru NOC. Analiza los datos de telemetría y da un diagnóstico técnico breve y acciones correctivas."
    user_query = f"Datos actuales de red: {data_summary}. ¿Qué problemas detectas y qué sugieres?"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_status == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Sin respuesta de IA.")
            time.sleep(2**i)
        except:
            time.sleep(2**i)
    return "Error de conexión con el núcleo de IA."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru NOC - AI Master Intelligence",
    page_icon="🛰️",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e6edf3; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    .ai-box { 
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #388bfd;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        box-shadow: 0 0 15px rgba(56, 139, 253, 0.2);
    }
    .logo-img { max-height: 80px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- GENERACIÓN DE DATOS ---
def get_data():
    now = datetime.now()
    return pd.DataFrame({
        'Timestamp': [now - timedelta(minutes=i) for i in range(50, 0, -1)],
        'EbNo': np.random.uniform(8.0, 13.0, 50),
        'Latency': np.random.uniform(540, 720, 50),
        'PacketLoss': np.random.uniform(0, 2.5, 50),
        'Traffic': np.random.uniform(20, 150, 50)
    })

def main():
    df = get_data()
    latest = df.iloc[-1]

    # --- ENCABEZADO CON LOGO ---
    col_l, col_r = st.columns([1, 4])
    with col_l:
        # Usando el nombre del archivo de logo proporcionado
        st.image("image_4b7f32.png", width=120)
    with col_r:
        st.title("MERU NOC: Inteligencia de Red Satelital")
        st.caption(f"Sistema Activo | Latencia de IA: 1.2s | {datetime.now().strftime('%H:%M:%S UTC')}")

    # --- MÉTRICAS PRINCIPALES ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eb/No Actual", f"{latest['EbNo']:.2f} dB", f"{latest['EbNo']-10:.1f}", delta_color="normal")
    m2.metric("Latencia Media", f"{int(latest['Latency'])} ms", "-5ms", delta_color="inverse")
    m3.metric("Packet Loss", f"{latest['PacketLoss']:.2f}%", "0.2%", delta_color="inverse")
    m4.metric("Throughput", f"{int(latest['Traffic'])} Mbps", "12 Mbps")

    st.divider()

    # --- CUERPO PRINCIPAL ---
    col_main, col_ai = st.columns([2, 1])

    with col_main:
        st.subheader("📊 Análisis de Telemetría Real-Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EbNo'], name="Eb/No", line=dict(color='#388bfd', width=3)))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Latency']/50, name="Latencia (Escalada)", line=dict(color='#f85149', dash='dot')))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de calor de nodos
        st.subheader("🌐 Estado de Nodos Periféricos")
        nodes = np.random.choice([0, 1, 2], size=(4, 8), p=[0.85, 0.1, 0.05])
        fig_heat = px.imshow(nodes, 
                            labels=dict(color="Estado"),
                            color_continuous_scale=['#238636', '#d29922', '#da3633'])
        fig_heat.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_ai:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.subheader("🧠 Diagnóstico de IA Meru")
        
        # Resumen para la IA
        summary = {
            "EbNo": round(latest['EbNo'], 2),
            "Loss": round(latest['PacketLoss'], 2),
            "Latency": int(latest['Latency']),
            "Trend": "Degradación detectada" if latest['EbNo'] < 9 else "Estable"
        }
        
        if st.button("🤖 Generar Informe de IA"):
            with st.spinner("Consultando al cerebro de red..."):
                analysis = call_gemini_analysis(json.dumps(summary))
                st.write(analysis)
        else:
            st.info("Haz clic para que la IA analice el estado actual de los enlaces.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("🚨 Registro de Eventos")
        for _ in range(3):
            st.warning(f"Aviso: Fluctuación en Nodo {np.random.randint(1,100)} detectada.")

    # --- TABLA CRUDA ---
    with st.expander("Ver Telemetría Completa"):
        st.table(df.tail(10))

if __name__ == "__main__":
    main()
