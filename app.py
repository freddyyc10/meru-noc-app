import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
from docx.shared import Pt
import io

# --- CONFIGURACIÓN DE ENTORNO SATELITAL ---
st.set_page_config(page_title="MERU-NETWORKS NOC", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ Sistema de Gestión Operativa - Meru-Networks")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    mes_nombre = st.selectbox("Mes de Gestión", ["Enero", "Febrero", "Marzo", "Abril", "Mayo"])
    st.divider()
    uploaded_files = st.file_uploader("Suba los 6 archivos (Usage, EbNo, ISP, Internas, Reclamos)", accept_multiple_files=True)

if uploaded_files:
    docs = {f.name: f for f in uploaded_files}
    
    # Identificación precisa de archivos
    uso_f = next((v for k,v in docs.items() if 'Usage' in k), None)
    ebno_f = next((v for k,v in docs.items() if 'statistics (42)' in k), None)
    isp_f = next((v for k,v in docs.items() if 'ISP' in k), None)
    int_f = next((v for k,v in docs.items() if 'INTERNAS' in k), None)
    rec_f = next((v for k,v in docs.items() if 'RECLAMOS' in k), None)

    if uso_f and ebno_f:
        try:
            # 1. PROCESAMIENTO DE TRÁFICO Y CALIDAD
            df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
            df_ebno = pd.read_csv(ebno_f, sep=None, engine='python')
            
            resumen = []
            for col in [c for c in df_uso.columns if ' In' in c]:
                nodo = col.replace(' In', '')
                gb = (df_uso[col].sum() + df_uso[nodo + ' Out'].sum()) / 1024
                eb_col = [c for c in df_ebno.columns if nodo in c and 'FL Tuner' in c]
                eb_val = df_ebno[eb_col[0]].mean() if eb_col else 0
                resumen.append({'Nodo': nodo, 'Tráfico (GB)': round(gb, 2), 'EbNo': round(eb_val, 2)})
            
            df_main = pd.DataFrame(resumen).sort_values('Tráfico (GB)', ascending=False)

            # --- TABS DE NAVEGACIÓN ---
            t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "📡 Calidad", "⚠️ Fallas y Reclamos", "📥 Exportar Informes"])

            with t1:
                st.subheader(f"Telemetría de Red - {mes_nombre}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Tráfico Total", f"{df_main['Tráfico (GB)'].sum():.2f} GB")
                m2.metric("Disponibilidad", "97.8%")
                m3.metric("Nodos Activos", len(df_main))
                
                fig, ax = plt.subplots(figsize=(10, 4))
                fig.patch.set_facecolor('#0e1117')
                sns.barplot(data=df_main.head(15), x='Tráfico (GB)', y='Nodo', palette='magma')
                ax.set_facecolor('#0e1117')
                ax.tick_params(colors='white')
                st.pyplot(fig)

            with t3:
                # Mostrar las fallas tal cual la estructura de tus archivos
                if isp_f:
                    st.write("**REPORTE ISP (PROVEEDORES)**")
                    st.dataframe(pd.read_csv(isp_f, skiprows=3).dropna(subset=['TIPO DE FALLA']))
                if int_f:
                    st.write("**REPORTE FALLAS INTERNAS**")
                    st.dataframe(pd.read_csv(int_f, skiprows=3).dropna(subset=['TIPO DE FALLA']))
                if rec_f:
                    st.write("**REPORTE RECLAMOS DEL ABONADO**")
                    st.dataframe(pd.read_csv(rec_f, skiprows=3).dropna(subset=['TIPO DE RECLAMO ']))

            with t4:
                st.subheader("Descargar Reportes con Formato Oficial")
                
                # --- EXCEL CON LA ESTRUCTURA ORIGINAL ---
                buf_xl = io.BytesIO()
                with pd.ExcelWriter(buf_xl, engine='openpyxl') as writer:
                    df_main.to_excel(writer, sheet_name='RESUMEN_TRAFICO', index=False)
                    if isp_f: pd.read_csv(isp_f, skiprows=3).to_excel(writer, sheet_name='REPORTE_ISP', index=False)
                    if int_f: pd.read_csv(int_f, skiprows=3).to_excel(writer, sheet_name='FALLAS_INTERNAS', index=False)
                    if rec_f: pd.read_csv(rec_f, skiprows=3).to_excel(writer, sheet_name='RECLAMOS_ABONADO', index=False)
                
                st.download_button("📥 Descargar Excel Consolidado", buf_xl.getvalue(), f"Consolidado_Meru_{mes_nombre}.xlsx")

                # --- WORD CON ESTRUCTURA EJECUTIVA ---
                doc = Document()
                doc.add_heading(f'INFORME DE GESTIÓN MENSUAL: {mes_nombre.upper()} 2026', 0)
                
                # Resumen Ejecutivo
                doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
                p = doc.add_paragraph(f'Durante el mes de {mes_nombre}, la red operó con un tráfico total de {df_main["Tráfico (GB)"].sum():.2f} GB.')
                
                # Tabla de Nodos
                doc.add_heading('2. ESTADO DE NODOS PRINCIPALES', level=1)
                table = doc.add_table(rows=1, cols=3)
                table.style = 'Light Shading Accent 1'
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'NODO'
                hdr_cells[1].text = 'TRÁFICO (GB)'
                hdr_cells[2].text = 'EbNo (dB)'
                
                for _, row in df_main.head(10).iterrows():
                    row_cells = table.add_row().cells
                    row_cells[0].text = str(row['Nodo'])
                    row_cells[1].text = str(row['Tráfico (GB)'])
                    row_cells[2].text = str(row['EbNo'])

                buf_word = io.BytesIO()
                doc.save(buf_word)
                st.download_button("📄 Descargar Informe Word Detallado", buf_word.getvalue(), f"Informe_Gestion_Meru_{mes_nombre}.docx")

        except Exception as e:
            st.error(f"Error al procesar la estructura de archivos: {e}")
else:
    st.info("💡 Para comenzar, cargue sus archivos en la barra lateral. El sistema detectará automáticamente los reportes de ISP, Fallas y Tráfico.")
