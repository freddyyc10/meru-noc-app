import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
import io

# --- CONFIGURACIÓN DE ENTORNO SATELITAL ---
st.set_page_config(page_title="MERU-NETWORKS NOC", layout="wide")

# CSS Corregido (Sin errores de parámetros)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #3b82f6; font-size: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #1f2937; border-radius: 5px; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Centro de Control Satelital Meru-Networks")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Panel de Configuración")
    mes_gestion = st.selectbox("Seleccione Mes:", ["Enero", "Febrero", "Marzo", "Abril"])
    st.divider()
    uploaded_files = st.file_uploader("Importar Reportes CSV/XLSX", accept_multiple_files=True)

if uploaded_files:
    # Diccionario de archivos
    docs = {f.name: f for f in uploaded_files}
    
    # Identificación por contenido (Blindado)
    uso_f = next((v for k,v in docs.items() if 'Usage' in k), None)
    ebno_f = next((v for k,v in docs.items() if 'statistics (42)' in k), None)
    isp_f = next((v for k,v in docs.items() if 'ISP' in k), None)
    internas_f = next((v for k,v in docs.items() if 'INTERNAS' in k), None)
    reclamos_f = next((v for k,v in docs.items() if 'RECLAMOS' in k), None)

    if uso_f and ebno_f:
        # 1. PROCESAMIENTO DE RED
        df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
        df_ebno = pd.read_csv(ebno_f, sep=None, engine='python')
        
        resumen = []
        for col in [c for c in df_uso.columns if ' In' in c]:
            nodo = col.replace(' In', '')
            gb = (df_uso[col].sum() + df_uso[nodo + ' Out'].sum()) / 1024
            eb_col = [c for c in df_ebno.columns if nodo in c and 'FL Tuner' in c]
            eb_val = df_ebno[eb_col[0]].mean() if eb_col else 0
            resumen.append({'Nodo': nodo, 'GB': round(gb, 2), 'EbNo': round(eb_val, 2)})
        
        df_final = pd.DataFrame(resumen).sort_values('GB', ascending=False)

        # 2. DASHBOARD DE MÉTRICAS
        m1, m2, m3 = st.columns(3)
        m1.metric("Disponibilidad Red", "97.8%", "Objetivo: 99%")
        m2.metric("Tráfico Total", f"{df_final['GB'].sum():.1f} GB")
        m3.metric("Nodos Críticos", len(df_final[df_final['EbNo'] < 9.5]))

        # 3. INTERFAZ DE PESTAÑAS (TABS)
        t1, t2, t3, t4 = st.tabs(["📊 Tráfico", "📡 Calidad Eb/No", "⚠️ Gestión de Fallas", "📥 Exportar"])

        with t1:
            st.subheader(f"Top Nodos - Gestión {mes_gestion}")
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#0e1117')
            sns.barplot(data=df_final.head(12), x='GB', y='Nodo', palette='viridis')
            ax.set_facecolor('#0e1117')
            ax.tick_params(colors='white')
            st.pyplot(fig)

        with t2:
            st.subheader("Análisis de Calidad de Telemetría")
            st.dataframe(df_final.style.highlight_between(left=0, right=9.5, subset=['EbNo'], color='#992222'))

        with t3:
            st.subheader("Consolidado de Incidencias")
            col_a, col_b = st.columns(2)
            if isp_f:
                with col_a:
                    st.write("**Eventos ISP (Satélite)**")
                    st.dataframe(pd.read_csv(isp_f, skiprows=3).dropna(subset=['TIPO DE FALLA']))
            if internas_f:
                with col_b:
                    st.write("**Fallas Internas (NOC)**")
                    st.dataframe(pd.read_csv(internas_f, skiprows=3).dropna(subset=['TIPO DE FALLA']))

        with t4:
            st.subheader("Generación de Entregables")
            # Lógica de Exportación Excel
            buffer_xl = io.BytesIO()
            with pd.ExcelWriter(buffer_xl,
