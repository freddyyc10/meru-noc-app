import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# --- CONFIGURACIÓN DE IA ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "TU_API_KEY_AQUÍ" 

def query_meru_ia(prompt, context):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"CONTEXTO TÉCNICO: {context}\n\nPREGUNTA OPERADOR: {prompt}"}]}],
        "systemInstruction": {"parts": [{"text": "Eres el Core de IA de Meru Networks. Analizas telemetría satelital iDirect. Detectas saturación de ancho de banda, caídas de Eb/No por lluvia y anomalías en el Bit Rate."}]}
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "⚠️ Error: Núcleo IA fuera de línea."

# --- LÓGICA DE LIMPIEZA IDIRECT (Basada en tu código) ---
def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if any(key in line for key in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
            skip_rows = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip_rows)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- CONFIGURACIÓN UI ---
st.set_page_config(page_title="MERU INTELLIGENCE HUB", layout="wide", page_icon="📡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    .stApp { background-color: #02060a; color: #00f2ff; font-family: 'JetBrains Mono', monospace; }
    .status-card { 
        background: rgba(0, 212, 255, 0.05); border: 1px solid #00d4ff; 
        padding: 20px; border-radius: 8px; text-align: center;
    }
    .metric-val { font-size: 2.2rem; font-weight: bold; color: #ffffff; text-shadow: 0 0 10px #00d4ff; }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ MERU NETWORKS | COMMAND CENTER v5.0")

# --- SIDEBAR: GESTIÓN DE ARCHIVOS ---
with st.sidebar:
    st.header("📥 DATA INGESTION")
    files = st.file_uploader("Cargar reportes iDirect (Múltiples CSV)", type="csv", accept_multiple_files=True)
    st.markdown("---")
    st.subheader("⚙️ LINK SPECS")
    freq = st.slider("Frecuencia (GHz)", 10.0, 30.0, 19.2)
    st.caption("Soporte para reportes de Tráfico y Señal.")

# --- PROCESAMIENTO CENTRAL ---
if files:
    all_data = []
    summary_for_ia = ""

    for f in files:
        df = get_clean_df(f)
        if df.empty: continue
        
        cols_text = " ".join(df.columns).lower()
        is_traffic = any(k in cols_text for k in ["octets", "bit rate"])
        
        # --- MÓDULO 1: ANÁLISIS DE TRÁFICO (Basado en tu app (1).py) ---
        if is_traffic:
            st.subheader(f"📊 Análisis de Consumo: {f.name}")
            sites = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
            report = []
            for s in sites:
                in_c = next((c for c in df.columns if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
                out_c = next((c for c in df.columns if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
                if in_c or out_c:
                    val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
                    val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
                    factor = (1024*1024) if "Octets" in str(in_c or out_c) else 1
                    report.append({"Estación": s, "In": val_in/factor, "Out": val_out/factor, "Total": (val_in+val_out)/factor})
            
            if report:
                res_df = pd.DataFrame(report).sort_values(by="Total", ascending=False)
                c1, c2 = st.columns(2)
                c1.plotly_chart(px.bar(res_df.head(10), x="Total", y="Estación", orientation='h', title="Top 10 Consumo", color_discrete_sequence=['#00d4ff']), use_container_width=True)
                c2.dataframe(res_df, use_container_width=True)
                summary_for_ia += f"Archivo {f.name} (Tráfico): Total {res_df['Total'].sum():.2f}. "

        # --- MÓDULO 2: ANÁLISIS DE SEÑAL Y EB/NO (Multi-CSV) ---
        else:
            st.subheader(f"📶 Histórico de Señal: {f.name}")
            stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
            selected = st.selectbox(f"Seleccione Estación ({f.name}):", stations)
            
            plot_cols = [c for c in df.columns if c.startswith(selected + "/")]
            time_col = next((c for c in df.columns if "Date" in c or "Time" in c), None)
            
            fig = go.Figure()
            for c in plot_cols:
                fig.add_trace(go.Scatter(x=df[time_col] if time_col else df.index, y=df[c], name=c.split('/')[-1]))
            
            fig.update_layout(template="plotly_dark", height=350, margin=dict(t=20, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Cálculo de FSPL dinámico
            fspl = 20 * np.log10(35786) + 20 * np.log10(freq) + 92.45
            st.write(f"**Pérdida de Espacio Libre (FSPL) calculada para {freq} GHz:** {fspl:.2f} dB")
            summary_for_ia += f"Archivo {f.name} (Señal): Estación {selected} analizada a {freq}GHz. "

    # --- MÓDULO 3: TERMINAL DE INTELIGENCIA ARTIFICIAL ---
    st.markdown("---")
    st.subheader("🧠 Meru AI Core: Análisis Predictivo")
    query = st.text_input("Consultar anomalías o Link Budget a la IA:", placeholder="Ej: ¿Hay riesgo de Rain Fade en la estación seleccionada?")
    
    if st.button("EJECUTAR ANÁLISIS NEURAL"):
        if query:
            with st.spinner("Analizando telemetría..."):
                respuesta = query_meru_ia(query, summary_for_ia)
                st.info(respuesta)
        else: st.warning("Escriba una pregunta técnica.")

else:
    # Pantalla de inicio llamativa
    st.markdown("""
        <div style="text-align:center; padding:100px;">
            <h2 style="color:#00d4ff;">ESPERANDO INGESTIÓN DE DATOS</h2>
            <p style="opacity:0.5;">Cargue los reportes iDirect CSV en la barra lateral para iniciar el comando.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<p style='text-align:center; opacity:0.2; font-size:10px;'>SECURED BY MERU NETWORKS SECURITY SYSTEM</p>", unsafe_allow_html=True)
