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
    system_prompt = (
        "Eres el Ingeniero Senior de Inteligencia Artificial de Meru NOC. "
        "Analiza los datos técnicos de telemetría satelital. Sé preciso, técnico y ofrece "
        "una recomendación de mitigación inmediata si los valores están fuera de rango (EbNo < 10)."
    )
    user_query = f"REPORTE DE TELEMETRÍA ACTUAL: {data_summary}. Diagnóstico técnico:"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Análisis completado sin observaciones.")
            # Backoff exponencial: 1s, 2s, 4s, 8s, 16s
            time.sleep(2**i)
        except Exception:
            time.sleep(2**i)
    return "⚠️ Error de enlace con el núcleo de IA. Verifique conexión del NOC."

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru NOC - AI Master Intelligence",
    page_icon="🛰️",
    layout="wide"
)

# --- ESTILOS Y LOGO ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e6edf3; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    .ai-box { 
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #388bfd;
        padding: 25px;
        border-radius: 15px;
        margin-top: 10px;
        box-shadow: 0 4px 20px rgba(56, 139, 253, 0.15);
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Generación de datos simulados realistas
@st.cache_data(ttl=10)
def get_telemetry_data():
    now = datetime.now()
    df = pd.DataFrame({
        'Timestamp': [now - timedelta(minutes=i) for i in range(60, 0, -1)],
        'EbNo': np.random.normal(11.5, 0.8, 60),
        'Latency': np.random.normal(580, 25, 60),
        'PacketLoss': np.random.uniform(0, 1.2, 60),
        'Throughput': np.random.uniform(80, 120, 60)
    })
    return df

def main():
    df = get_telemetry_data()
    latest = df.iloc[-1]

    # --- ENCABEZADO ---
    col_header_1, col_header_2 = st.columns([1, 4])
    
    with col_header_1:
        # LOGO MERU (Usamos un placeholder visual robusto para evitar errores de archivo)
        st.markdown("""
            <div style="background-color:#388bfd; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:24px; letter-spacing:2px;">
                MERU
            </div>
            """, unsafe_allow_html=True)
            
    with col_header_2:
        st.title("Network Operations Center (NOC) | AI Intelligence")
        st.markdown(f"**Estado del Sistema:** <span class='status-badge' style='background:#238636;'>OPERATIVO</span> | UTC: {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)

    st.write("---")

    # --- KPI METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eb/No (Signal)", f"{latest['EbNo']:.2f} dB", f"{latest['EbNo']-11:.1f}", delta_color="normal")
    m2.metric("Latencia Media", f"{int(latest['Latency'])} ms", "-12ms", delta_color="inverse")
    m3.metric("Packet Loss", f"{latest['PacketLoss']:.2f}%", "0.05%", delta_color="inverse")
    m4.metric("Throughput", f"{int(latest['Throughput'])} Mbps", "5 Mbps")

    # --- CUERPO PRINCIPAL ---
    col_main, col_ai = st.columns([2, 1])

    with col_main:
        st.subheader("📊 Análisis de Enlace Satelital")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['EbNo'], name="Calidad Eb/No", line=dict(color='#388bfd', width=3)))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Throughput']/10, name="Carga (Escalada)", line=dict(color='#f1e05a', dash='dot')))
        fig.update_layout(
            template="plotly_dark", 
            height=400, 
            margin=dict(l=0,r=0,t=20,b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🌐 Topología de Nodos Globales")
        # Simulación de estados de nodos
        node_status = np.random.choice(["Online", "Warning", "Critical"], size=10, p=[0.8, 0.15, 0.05])
        node_cols = st.columns(5)
        for i, status in enumerate(node_status):
            color = "#238636" if status == "Online" else "#d29922" if status == "Warning" else "#da3633"
            node_cols[i % 5].markdown(f"<div style='border-left: 4px solid {color}; padding:5px; background:#161b22; margin:2px;'>Node-{i+100}<br><small>{status}</small></div>", unsafe_allow_html=True)

    with col_ai:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.subheader("🧠 Diagnóstico Gemini AI")
        
        # Preparar resumen técnico para la IA
        summary_data = {
            "signal_quality": f"{latest['EbNo']:.2f} dB",
            "latency": f"{latest['Latency']:.0f}ms",
            "packet_loss": f"{latest['PacketLoss']:.2f}%",
            "traffic_load": f"{latest['Throughput']:.0f}%"
        }
        
        st.write("El motor Gemini 2.5 Flash está listo para procesar la telemetría actual.")
        
        if st.button("🤖 Generar Análisis Inteligente", use_container_width=True):
            with st.spinner("Analizando patrones de red..."):
                analysis = call_gemini_analysis(json.dumps(summary_data))
                st.markdown(f"**Resultado del Análisis:**\n\n{analysis}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("🔔 Alertas Recientes")
        st.error("Alerta: Degradación de EbNo detectada en Sector 4 (Simulado)")
        st.info("Info: Backup de configuración completado a las 01:00 UTC")

if __name__ == "__main__":
    main()
