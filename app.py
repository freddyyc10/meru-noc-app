import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURACIÓN DE MODELO ---
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"
API_KEY = "TU_API_KEY" # Se recomienda usar st.secrets

# --- INICIALIZACIÓN DE BASE DE DATOS DE TICKETS ---
if 'ticket_db' not in st.session_state:
    st.session_state.ticket_db = pd.DataFrame(columns=[
        "ID", "Fecha", "Estación", "Categoría", "Prioridad", "Descripción", "Estado"
    ])

# --- FUNCIONES DE SOPORTE ---
def query_gemini_expert(prompt, context):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": f"SISTEMA NOC MERU. Contexto: {context}\n\nConsulta: {prompt}"}]}],
        "systemInstruction": {"parts": [{"text": "Eres el Ingeniero Principal de Meru Networks. Analiza telemetría iDirect y genera reportes de incidentes."}]}
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Error de conexión con el núcleo de inteligencia."

def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if any(key in line for key in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
            skip_rows = i
            break
    file.seek(0)
    df = pd.read_csv(file, skiprows=skip_rows)
    df.columns = [str(c).strip().replace('"', '') for c in df.columns]
    return df

# --- INTERFAZ NOC (UI/UX) ---
st.set_page_config(page_title="MERU COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #010409; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: #0d1117; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #58a6ff; font-family: 'JetBrains Mono'; }
    .ticket-card { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .status-alert { color: #ff7b72; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# --- PANEL SUPERIOR ---
st.title("🛰️ MERU GLOBAL OPERATIONS")
tabs = st.tabs(["📊 Telemetría en Vivo", "🎫 Gestión de Tickets", "🧠 Inteligencia Core", "💾 Base de Datos"])

# --- TAB 1: TELEMETRÍA Y ANÁLISIS CSV ---
with tabs[0]:
    col_side, col_main = st.columns([1, 4])
    
    with col_side:
        st.subheader("Ingesta de Datos")
        files = st.file_uploader("Cargar statistics.csv", accept_multiple_files=True)
        freq_ref = st.number_input("Freq Ref (GHz)", 19.2)

    if files:
        for f in files:
            df = get_clean_df(f)
            with col_main:
                st.markdown(f"### 📡 Análisis: {f.name}")
                stations = sorted(list(set([c.split('/')[0] for c in df.columns if '/' in c])))
                
                # Resumen rápido
                c1, c2, c3 = st.columns(3)
                # Detección de tipo de reporte
                is_traffic = "Octets" in " ".join(df.columns)
                
                if is_traffic:
                    total_traffic = 0
                    for s in stations:
                        col_in = next((c for c in df.columns if c.startswith(s + "/") and "In" in c), None)
                        if col_in: total_traffic += pd.to_numeric(df[col_in], errors='coerce').sum()
                    c1.metric("Tráfico Total", f"{total_traffic/(1024*1024):.2f} MB")
                
                # Gráfico Evolutivo
                target_station = st.selectbox(f"Estación foco ({f.name})", stations)
                plot_cols = [c for c in df.columns if c.startswith(target_station + "/")]
                fig = px.line(df, y=plot_cols, title=f"Series de Tiempo: {target_station}")
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: SISTEMA DE TICKETS (NUEVO) ---
with tabs[1]:
    st.header("🎫 Registro de Incidentes (Tickets)")
    
    with st.expander("➕ Crear Nuevo Ticket"):
        with st.form("new_ticket"):
            t_estacion = st.text_input("Estación Afectada")
            t_cat = st.selectbox("Categoría", ["Eb/No Bajo", "Saturación BW", "Outage Total", "Falla de Hardware"])
            t_pri = st.select_slider("Prioridad", ["Baja", "Media", "Alta", "CRÍTICA"])
            t_desc = st.text_area("Descripción del problema")
            if st.form_submit_button("Generar Ticket"):
                new_id = f"TIC-{len(st.session_state.ticket_db)+1001}"
                new_row = {
                    "ID": new_id, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Estación": t_estacion, "Categoría": t_cat, "Prioridad": t_pri,
                    "Descripción": t_desc, "Estado": "Abierto"
                }
                st.session_state.ticket_db = pd.concat([st.session_state.ticket_db, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Ticket {new_id} registrado exitosamente.")

    # Visualización de Tickets
    st.subheader("Tickets Activos")
    if not st.session_state.ticket_db.empty:
        for _, row in st.session_state.ticket_db.iterrows():
            color = "red" if row['Prioridad'] == "CRÍTICA" else "orange"
            st.markdown(f"""
                <div class="ticket-card">
                    <span style="color:{color}">● {row['ID']}</span> | <b>{row['Estación']}</b> | {row['Fecha']} <br>
                    <small>{row['Categoría']} - {row['Prioridad']}</small><br>
                    <i>{row['Descripción']}</i>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No hay tickets pendientes.")

# --- TAB 3: IA EXPERT ---
with tabs[2]:
    st.header("🧠 Meru AI Analysis")
    user_p = st.text_area("Describa el problema observado para diagnóstico de IA:")
    if st.button("Consultar Núcleo"):
        contexto = f"Tickets activos: {len(st.session_state.ticket_db)}. Última telemetría analizada."
        respuesta = query_gemini_expert(user_p, contexto)
        st.write(respuesta)

# --- TAB 4: BASE DE DATOS ---
with tabs[3]:
    st.header("💾 Exportar Base de Datos")
    st.write("Historial de operaciones acumulado:")
    st.dataframe(st.session_state.ticket_db, use_container_width=True)
    
    csv_tickets = st.session_state.ticket_db.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Base de Datos de Tickets", csv_tickets, "tickets_meru.csv", "text/csv")

st.markdown("<p style='text-align:center; opacity:0.3; margin-top:50px;'>MERU NETWORKS NOC - OPERATIONAL SECURE SYSTEM</p>", unsafe_allow_html=True)
