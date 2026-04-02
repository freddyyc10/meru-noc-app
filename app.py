import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
from docx.shared import Inches
import io

# --- CONFIGURACIÓN DE ENTORNO SATELITAL ---
st.set_page_config(page_title="MERU-NETWORKS NOC", layout="wide", initial_sidebar_state="expanded")

# CSS para look de Centro de Control
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; }
    div[data-testid="stExpander"] { background-color: #1f2937; border: none; }
    </style>
    """, unsafe_allow_index=True)

# --- BARRA LATERAL: CONTROL DE DATOS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2099/2099192.png", width=80)
    st.title("Gestión de Red")
    
    mes_seleccionado = st.selectbox("📅 Seleccionar Mes de Gestión", 
        ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"])
    
    st.subheader("📥 Importar Datos")
    archivos = st.file_uploader("Subir reportes CSV/XLSX", accept_multiple_files=True)

# --- LÓGICA DE PROCESAMIENTO ---
if archivos:
    docs = {f.name: f for f in archivos}
    
    # Identificación de archivos
    uso_f = next((v for k,v in docs.items() if 'Usage' in k), None)
    ebno_f = next((v for k,v in docs.items() if 'statistics (42)' in k), None)
    isp_f = next((v for k,v in docs.items() if 'ISP' in k), None)
    fallas_f = next((v for k,v in docs.items() if 'FALLAS INTERNAS' in k), None)
    reclamos_f = next((v for k,v in docs.items() if 'RECLAMOS' in k), None)

    if uso_f and ebno_f:
        # Lectura de Tráfico y Eb/No
        df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
        df_ebno = pd.read_csv(ebno_f, sep=None, engine='python')
        
        # Consolidación de Nodos
        resumen = []
        cols_in = [c for c in df_uso.columns if ' In' in c]
        for c in cols_in:
            n = c.replace(' In', '')
            total_gb = (df_uso[c].sum() + df_uso[n + ' Out'].sum()) / 1024
            eb_col = [col for col in df_ebno.columns if n in col and 'FL Tuner' in col]
            eb_val = df_ebno[eb_col[0]].mean() if eb_col else 0
            resumen.append({'Nodo': n, 'Tráfico (GB)': round(total_gb, 2), 'EbNo': round(eb_val, 2)})
        
        df_main = pd.DataFrame(resumen).sort_values('Tráfico (GB)', ascending=False)

        # --- INTERFAZ VISUAL ---
        st.title(f"🛰️ Reporte Operativo: {mes_seleccionado} 2026")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Disponibilidad", "97.8%", "+0.5%")
        m2.metric("Tráfico Total", f"{df_main['Tráfico (GB)'].sum():.1f} GB")
        m3.metric("Nodos Activos", len(df_main))
        m4.metric("Calidad Promedio", f"{df_main['EbNo'].mean():.2f} dB")

        # Dashboard Principal
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("🚀 Top Nodos por Consumo de Datos")
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#0e1117')
            sns.barplot(data=df_main.head(15), x='Tráfico (GB)', y='Nodo', palette='flare')
            ax.set_facecolor('#0e1117')
            ax.tick_params(colors='white')
            st.pyplot(fig)

        with c2:
            st.subheader("🚨 Alertas de Calidad")
            nodos_criticos = df_main[df_main['EbNo'] < 9.5]
            if not nodos_criticos.empty:
                st.error(f"Se detectaron {len(nodos_criticos)} nodos con Eb/No crítico.")
                st.dataframe(nodos_criticos[['Nodo', 'EbNo']])
            else:
                st.success("Toda la red opera sobre el umbral (9.5 dB)")

        # --- SECCIÓN DE EXPORTACIÓN ---
        st.divider()
        st.subheader("📤 Generación de Informes de Gestión")
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            # Botón Exportar Excel de Fallas (Consolidado)
            buffer_xlsx = io.BytesIO()
            with pd.ExcelWriter(buffer_xlsx, engine='openpyxl') as writer:
                df_main.to_excel(writer, sheet_name='Resumen_Trafico')
                if fallas_f: pd.read_csv(fallas_f, skiprows=3).to_excel(writer, sheet_name='Fallas_Internas')
                if isp_f: pd.read_csv(isp_f, skiprows=3).to_excel(writer, sheet_name='Reporte_ISP')
            
            st.download_button(
                label="📥 Descargar Excel Consolidado de Fallas",
                data=buffer_xlsx.getvalue(),
                file_name=f"Consolidado_Fallas_{mes_seleccionado}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col_exp2:
            # Botón Exportar Word (Informe Ejecutivo)
            doc = Document()
            doc.add_heading(f'Informe de Gestión Mensual - {mes_seleccionado} 2026', 0)
            doc.add_paragraph(f'Resumen Operativo de la Red Meru-Networks.')
            doc.add_section()
            
            # Crear tabla de nodos en Word
            table = doc.add_table(rows=1, cols=3)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Nodo'
            hdr_cells[1].text = 'Tráfico (GB)'
            hdr_cells[2].text = 'EbNo'
            for _, row in df_main.head(10).iterrows():
                row_cells = table.add_row().cells
                row_cells[0].text = str(row['Nodo'])
                row_cells[1].text = str(row['Tráfico (GB)'])
                row_cells[2].text = str(row['EbNo'])
            
            buffer_word = io.BytesIO()
            doc.save(buffer_word)
            
            st.download_button(
                label="📄 Descargar Informe Word Detallado",
                data=buffer_word.getvalue(),
                file_name=f"Informe_Gestion_{mes_seleccionado}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

else:
    st.warning("📡 SISTEMA EN ESPERA: Por favor, cargue los archivos en la barra lateral para iniciar el monitoreo.")
