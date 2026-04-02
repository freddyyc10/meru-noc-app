import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
from docx.shared import Inches
import io

# --- CONFIGURACIÓN DE INTERFAZ SATELITAL ---
st.set_page_config(page_title="MERU-NETWORKS NOC", layout="wide")

# Estética Dark Mode para Centro de Operaciones
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    div[data-testid="stExpander"] { background-color: #1f2937; border: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1f2937; 
        border-radius: 5px; 
        color: white; 
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Centro de Gestión de Red (NOC) - Meru-Networks")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2099/2099192.png", width=70)
    st.header("Configuración")
    mes_nombre = st.selectbox("Mes de Gestión", ["Enero", "Febrero", "Marzo", "Abril", "Mayo"])
    st.divider()
    uploaded_files = st.file_uploader("📂 Importar Datos CSV/XLSX", accept_multiple_files=True)

if uploaded_files:
    # Mapeo de archivos subidos
    docs = {f.name: f for f in uploaded_files}
    
    # Identificación inteligente por palabras clave en el nombre
    uso_f = next((v for k,v in docs.items() if 'Usage' in k or 'VNO' in k), None)
    ebno_f = next((v for k,v in docs.items() if 'statistics (42)' in k), None)
    isp_f = next((v for k,v in docs.items() if 'ISP' in k), None)
    int_f = next((v for k,v in docs.items() if 'INTERNAS' in k), None)
    rec_f = next((v for k,v in docs.items() if 'RECLAMOS' in k), None)

    # Solo procesar si tenemos lo básico: Tráfico y Calidad
    if uso_f and ebno_f:
        try:
            # 1. PROCESAMIENTO TÉCNICO
            df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
            df_ebno = pd.read_csv(ebno_f, sep=None, engine='python')
            
            resumen = []
            for col in [c for c in df_uso.columns if ' In' in c]:
                nodo = col.replace(' In', '')
                gb = (df_uso[col].sum() + df_uso[nodo + ' Out'].sum()) / 1024
                # Buscar FL Eb/No
                eb_col = [c for c in df_ebno.columns if nodo in c and 'FL Tuner' in c]
                eb_val = df_ebno[eb_col[0]].mean() if eb_col else 0
                resumen.append({'Nodo': nodo, 'GB': round(gb, 2), 'EbNo': round(eb_val, 2)})
            
            df_main = pd.DataFrame(resumen).sort_values('GB', ascending=False)

            # 2. INDICADORES (KPIs)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Status Red", "Online", "📡")
            k2.metric("Tráfico Total", f"{df_main['GB'].sum():.1f} GB")
            k3.metric("Nodos < 9.5dB", len(df_main[df_main['EbNo'] < 9.5]))
            k4.metric("Mes", mes_nombre)

            # 3. PESTAÑAS DE NAVEGACIÓN
            t1, t2, t3, t4 = st.tabs(["📊 Tráfico", "📡 Salud de Red", "⚠️ Fallas y Reclamos", "📥 Exportar"])

            with t1:
                st.subheader("Carga por Nodo (Top 12)")
                fig, ax = plt.subplots(figsize=(10, 4))
                fig.patch.set_facecolor('#0e1117')
                sns.barplot(data=df_main.head(12), x='GB', y='Nodo', palette='viridis')
                ax.set_facecolor('#0e1117')
                ax.tick_params(colors='white')
                st.pyplot(fig)

            with t2:
                st.subheader("Monitoreo de Calidad FL Eb/No")
                # Resaltar en rojo los que están por debajo de 9.5
                st.dataframe(df_main.style.highlight_between(left=0, right=9.5, subset=['EbNo'], color='#441111'))
                st.info("💡 Los valores resaltados indican necesidad de ajuste de apuntamiento o revisión de BUC.")

            with t3:
                st.subheader("Histórico de Incidencias")
                c_a, c_b = st.columns(2)
                if isp_f:
                    with c_a:
                        st.write("**Reporte ISP (Satelital)**")
                        st.dataframe(pd.read_csv(isp_f, skiprows=3).dropna(how='all', axis=0).head(10))
                if int_f:
                    with c_b:
                        st.write("**Fallas Internas (NOC)**")
                        st.dataframe(pd.read_csv(int_f, skiprows=3).dropna(how='all', axis=0).head(10))

            with t4:
                st.subheader("Generación Automática de Entregables")
                
                # --- EXPORTAR EXCEL ---
                buffer_xl = io.BytesIO()
                with pd.ExcelWriter(buffer_xl, engine='openpyxl') as writer:
                    df_main.to_excel(writer, index=False, sheet_name='Trafico_Calidad')
                    if isp_f: pd.read_csv(isp_f, skiprows=3).to_excel(writer, index=False, sheet_name='ISP')
                    if int_f: pd.read_csv(int_f, skiprows=3).to_excel(writer, index=False, sheet_name='Fallas_Internas')
                
                st.download_button(
                    label="📥 Descargar Consolidado Excel",
                    data=buffer_xl.getvalue(),
                    file_name=f"Consolidado_NOC_{mes_nombre}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # --- EXPORTAR WORD ---
                doc = Document()
                doc.add_heading(f'Informe de Gestión Satelital - {mes_nombre}', 0)
                doc.add_paragraph(f'Durante el mes se procesó un tráfico total de {df_main["GB"].sum():.2f} GB.')
                
                buf_word = io.BytesIO()
                doc.save(buf_word)
                st.download_button(
                    label="📄 Descargar Informe Word",
                    data=buf_word.getvalue(),
                    file_name=f"Informe_Ejecutivo_{mes_nombre}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"Error técnico: {e}")
    else:
        st.warning("🔄 Por favor, suba los archivos de 'Usage' y 'statistics' para iniciar el análisis.")
else:
    st.write("### 👋 Bienvenida al Sistema NOC Meru-Networks")
    st.write("Arrastre los archivos mensuales al panel de la izquierda para generar la telemetría.")
