import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Meru Networks - Intelligence Hub",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS para mantener la estética corporativa de Meru
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #3f4494; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button {
        background-color: #3f4494;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00aeef;
        color: white;
    }
    .ai-box {
        background-color: #f0f7ff;
        border-left: 5px solid #00aeef;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INTELIGENCIA ARTIFICIAL ---
API_KEY = "" # El entorno inyecta la clave automáticamente

def get_ai_diagnosis(data_summary):
    """Consulta al modelo Gemini para análisis de red."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    prompt = f"""
    Eres un experto en redes satelitales de Meru Networks. 
    Analiza la siguiente telemetría y genera un diagnóstico breve, técnico y con pasos de mitigación:
    {data_summary}
    Responde en español profesional.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "Analista Senior de NOC de Meru Networks."}]}
    }
    
    # Reintentos con exponencial backoff
    for wait_time in [1, 2, 4]:
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            time.sleep(wait_time)
        except:
            time.sleep(wait_time)
    return "Error al conectar con el motor de IA. Intente de nuevo."

# --- INTERFAZ PRINCIPAL ---

# Header Corporativo
col_logo, col_text = st.columns([1, 4])
with col_text:
    st.markdown("# <span style='color:#00aeef'>MERU</span> NETWORKS", unsafe_allow_html=True)
    st.markdown("### NOC Operational Intelligence Hub")

st.divider()

# Sidebar para controles
with st.sidebar:
    st.image("https://www.meru.com.ve/wp-content/uploads/2021/05/Logo-Meru-Networks-Vertical.png", width=150) # Logo placeholder
    st.header("Configuración")
    uploaded_file = st.file_uploader("Cargar Telemetría (CSV)", type=["csv"])
    umbral = st.slider("Umbral Crítico de Eb/No", 5.0, 15.0, 8.5)
    st.info("Sube archivos de exportación de iDirect o Gilat.")

if uploaded_file:
    try:
        # Carga de datos
        df = pd.read_csv(uploaded_file)
        
        # Selección inteligente de columnas
        cols = df.columns.tolist()
        val_col = next((c for c in cols if any(x in c.lower() for x in ['valor', 'value', 'eb', 'rate', 'data'])), cols[-1])
        time_col = next((c for c in cols if any(x in c.lower() for x in ['fecha', 'date', 'time', 'tiempo'])), cols[0])
        
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
        df = df.dropna(subset=[val_col])

        # Métricas principales
        m1, m2, m3, m4 = st.columns(4)
        avg_val = df[val_col].mean()
        max_val = df[val_col].max()
        min_val = df[val_col].min()
        
        m1.metric("Promedio Red", f"{avg_val:.2f}")
        m2.metric("Pico Máximo", f"{max_val:.2f}")
        m3.metric("Mínimo Detectado", f"{min_val:.2f}")
        
        estado = "ÓPTIMO" if avg_val > umbral else "CRÍTICO"
        color_estado = "normal" if estado == "ÓPTIMO" else "inverse"
        m4.metric("Estado de Salud", estado, delta=f"{avg_val - umbral:.1f} dB", delta_color=color_estado)

        # Gráfico interactivo
        st.subheader("Análisis de Tendencias")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[time_col], 
            y=df[val_col],
            mode='lines+markers',
            line=dict(color='#3f4494', width=2),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor='rgba(63, 68, 148, 0.1)'
        ))
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(title=val_col, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig, use_container_width=True)

        # Botón de IA
        st.divider()
        if st.button("🤖 ANALIZAR CON INTELIGENCIA ARTIFICIAL"):
            with st.spinner("Meru AI procesando telemetría..."):
                resumen = f"Promedio: {avg_val:.2f}, Máximo: {max_val:.2f}, Mínimo: {min_val:.2f}, Total Registros: {len(df)}"
                diagnostico = get_ai_diagnosis(resumen)
                st.markdown(f"""
                    <div class="ai-box">
                        <h4 style="margin-top:0; color:#1e40af;">Reporte de Diagnóstico Meru AI</h4>
                        <p style="white-space: pre-wrap;">{diagnostico}</p>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el CSV tenga columnas numéricas.")
else:
    # Vista vacía
    st.markdown("""
        <div style="text-align: center; padding: 100px 0px; border: 2px dashed #e2e8f0; border-radius: 20px;">
            <h2 style="color:#94a3b8;">Sistema Listo</h2>
            <p style="color:#cbd5e1;">Cargue un archivo CSV de telemetría para comenzar el monitoreo en tiempo real.</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
st.caption("© 2024 Meru Networks S.A. | Gerencia de Operaciones Satelitales")
