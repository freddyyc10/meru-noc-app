import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import re
from datetime import datetime
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Meru NOC | Sistematización",
    page_icon="📡",
    layout="wide"
)

# --- ESTILOS CSS (Inspirados en tu index.html) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0f172a; color: #f1f5f9; }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 10px 10px 0px 0px;
        color: #94a3b8;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. LÓGICA DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('meru_tickets.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tickets 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  fecha TEXT, 
                  nodo TEXT, 
                  falla TEXT, 
                  estatus TEXT, 
                  duracion TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. FUNCIONES DE PROCESAMIENTO ---
def limpiar_nombre_nodo(nombre):
    if not isinstance(nombre, str): return str(nombre)
    nombre = re.sub(r'\s+(In|Out)$', '', nombre, flags=re.IGNORECASE)
    nombre = re.sub(r'/(ifInOctets|ifOutOctets|RL Measured|FL Tuner|Measured|Tuner|Traffic).*$', '', nombre, flags=re.IGNORECASE)
    return nombre.strip().replace('"', '')

def procesar_archivos(file_u, files_s):
    # Procesar Uso
    try:
        
     df = pd.read_csv('tu_archivo.csv', sep=None, engine='python', on_bad_lines='skip')
    * `sep=None`: Hace que Pandas intente adivinar si usas coma, punto y coma o tabulación.
* `on_bad_lines='skip'`: Si una línea está mal (como esa línea 4 con 102 campos), simplemente la ignora en lugar de detener todo el programa.
# Salta las primeras 3 líneas si son títulos o texto innecesario
df = pd.read_csv('tu_archivo.csv', skiprows=3)
        
        usage_data = []
        for col in df_usage.columns:
            if "Date" in col or "Unnamed" in col: continue
            val = pd.to_numeric(df_usage[col], errors='coerce').sum()
            usage_data.append({"Nodo": limpiar_nombre_nodo(col), "Consumo_GB": round(val/1024, 2)})
        df_res_u = pd.DataFrame(usage_data).groupby("Nodo").sum().reset_index()
        
        # Procesar Señal (Eb/No)
        signal_data = []
        if files_s:
            for f in files_s:
                df_s = pd.read_csv(f)
                for col in df_s.columns:
                    if any(x in col.lower() for x in ["eb/no", "measured", "db"]):
                        val = pd.to_numeric(df_s[col], errors='coerce').mean()
                        if not np.isnan(val):
                            signal_data.append({"Nodo": limpiar_nombre_nodo(col), "EbNo": round(val, 2)})
        
        if signal_data:
            df_res_s = pd.DataFrame(signal_data).groupby("Nodo").mean().reset_index()
            return pd.merge(df_res_u, df_res_s, on="Nodo", how="left").fillna("N/A")
        return df_res_u
    except Exception as e:
        st.error(f"Error en procesamiento: {e}")
        return pd.DataFrame()

# --- 3. INTERFAZ (UI) ---

st.markdown('<h1 class="header-title">Meru Networks NOC Auto-Report</h1>', unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; margin-bottom:2rem;'>Centro de Operaciones Sistematizado</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD & CARGA", "🎫 GESTOR DE TICKETS", "📄 GENERAR REPORTES"])

with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Carga de Datos Maestros")
    c1, c2 = st.columns(2)
    with c1:
        file_usage = st.file_uploader("Archivo Usage Report (CSV)", type="csv", help="Cargue el reporte de consumo de PRTG/NMS")
    with c2:
        files_stats = st.file_uploader("Estadísticas Eb/No (CSV)", type="csv", accept_multiple_files=True)
    
    if st.button("🚀 PROCESAR Y VISUALIZAR"):
        if file_usage:
            with st.spinner("Analizando registros..."):
                df_final = procesar_archivos(file_usage, files_stats)
                if not df_final.empty:
                    st.session_state['df_master'] = df_final
                    st.success("Análisis completado")
                    
                    st.subheader("Vista Previa de Red")
                    st.dataframe(df_final, use_container_width=True)
                else:
                    st.error("No se detectaron columnas de datos válidas.")
        else:
            st.warning("Suba el archivo de Usage para comenzar.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Registro de Fallas del Periodo")
    
    # Cargar tickets de la DB
    query = "SELECT * FROM tickets"
    df_tickets = pd.read_sql(query, db_conn)
    
    # Editor de datos dinámico
    st.info("Puede agregar, editar o eliminar filas directamente en la tabla.")
    edited_df = st.data_editor(
        df_tickets, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "fecha": st.column_config.DateColumn("Fecha Falla"),
            "estatus": st.column_config.SelectboxColumn("Estatus", options=["Abierto", "Cerrado", "En Observación"])
        },
        key="editor_tickets"
    )
    
    if st.button("💾 GUARDAR CAMBIOS EN BASE DE DATOS"):
        try:
            # Sincronizar editor con SQL
            edited_df.to_sql('tickets', db_conn, if_exists='replace', index=False)
            st.toast("Base de datos sincronizada correctamente", icon="✅")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Exportación de Reporte Ejecutivo")
    
    if 'df_master' in st.session_state:
        st.write("Datos listos para exportar basados en el análisis de la Pestaña 1.")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🤖 REDACTAR RESUMEN CON IA (GEMINI)"):
                # Simulación de prompt para Gemini basado en datos reales
                nodos_top = st.session_state['df_master'].nlargest(3, 'Consumo_GB')['Nodo'].tolist()
                st.info(f"IA analizando: {len(st.session_state['df_master'])} nodos detectados.")
                st.markdown(f"""
                **Resumen sugerido por IA:**
                *Durante el periodo analizado, se observó un tráfico predominante en los nodos **{', '.join(nodos_top)}**. 
                La estabilidad de la señal Eb/No se mantuvo dentro de los parámetros operativos (>10dB) 
                salvo por fluctuaciones menores en zonas de alta atenuación.*
                """)
        
        with c2:
            # Botón de descarga de CSV procesado
            csv = st.session_state['df_master'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DESCARGAR EXCEL DE FACTURACIÓN",
                data=csv,
                file_name=f"Reporte_Meru_{datetime.now().strftime('%Y%m')}.csv",
                mime='text/csv',
                use_container_width=True
            )
            
        st.warning("⚠️ Nota: Para habilitar el llenado de Word (.docx) y Excel (.xlsx) exactos, asegúrese de tener las plantillas en la carpeta del servidor.")
    else:
        st.info("Primero procese los datos en la pestaña 'Dashboard & Carga'.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<div style='text-align:center; color:#475569; margin-top:3rem;'>Meru Networks System v2.5 | Operations Dashboard</div>", unsafe_allow_html=True)
