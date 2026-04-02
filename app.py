import streamlit as st
import pandas as pd
import io
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Meru NOC - Generador de Informes", layout="wide", page_icon="📊")

def clean_meru_csv(file, expected_keywords):
    """Limpia archivos CSV que tienen metadatos en las primeras filas"""
    if file is None: return None
    try:
        # Leer todo el archivo
        content = file.getvalue().decode('utf-8')
        df_raw = pd.read_csv(io.StringIO(content), header=None)
        
        # Buscar la fila que contiene las palabras clave esperadas
        header_row_idx = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(row.astype(str).values).upper()
            if all(kw.upper() in row_str for kw in expected_keywords):
                header_row_idx = i
                break
        
        # Re-leer desde esa fila
        df = pd.read_csv(io.StringIO(content), skiprows=header_row_idx)
        df.columns = [str(c).strip().upper() for c in df.columns]
        # Eliminar filas totalmente vacías
        df = df.dropna(how='all').reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error procesando {file.name}: {e}")
        return None

def generate_word_report(df_internas, df_isp, df_reclamos):
    """Genera el Informe de Gestión Mensual en formato Word"""
    doc = Document()
    
    # Título Principal
    title = doc.add_heading('INFORME DE GESTIÓN MENSUAL: RED SATELITAL MERU', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Datos de encabezado
    p = doc.add_paragraph()
    p.add_run('Periodo: ').bold = True
    p.add_run('01 de marzo de 2026 al 31 de marzo de 2026\n')
    p.add_run('Departamento: ').bold = True
    p.add_run('Operaciones de Red (NOC) / Soporte Técnico')
    
    # 1. Resumen Ejecutivo
    doc.add_heading('1. RESUMEN EJECUTIVO', level=1)
    disp = 98.5 # Valor base ejemplo
    total_fallas = len(df_internas) + len(df_isp)
    doc.add_paragraph(
        f"Durante el mes de marzo de 2026, la red operó con un cumplimiento del SLA del {disp}%. "
        f"Se registraron un total de {total_fallas} eventos técnicos, de los cuales "
        f"{len(df_isp)} correspondieron a incidencias de proveedores externos (ISP) y {len(df_internas)} a fallas internas de infraestructura."
    )
    
    # 2. Fallas Internas
    doc.add_heading('2. REPORTE DE FALLAS INTERNAS', level=1)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'FECHA'
    hdr_cells[1].text = 'TIPO DE FALLA'
    hdr_cells[2].text = 'AFECTADOS'
    hdr_cells[3].text = 'DURACIÓN'
    
    # Agregar hasta 10 filas para no saturar el doc
    for i, row in df_internas.head(10).iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row.get('FECHA DE FALLA', row.get('FECHA', 'N/A')))
        row_cells[1].text = str(row.get('TIPO DE FALLA', 'N/A'))
        row_cells[2].text = str(row.get('ABONADOS AFECTADOS', 'N/A'))
        row_cells[3].text = str(row.get('DURACIÓN DE FALLA', 'N/A'))

    # 3. Reclamos Abonados
    doc.add_heading('3. GESTIÓN DE RECLAMOS DE ABONADOS', level=1)
    doc.add_paragraph(f"Total de reclamos atendidos: {len(df_reclamos)}")
    
    # Conclusiones
    doc.add_heading('4. CONCLUSIONES', level=1)
    doc.add_paragraph("Se recomienda mantener el monitoreo preventivo ante la temporada de lluvias.")
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ STREAMLIT ---
st.title("📡 Meru NOC: Analizador y Generador de Reportes")
st.info("Cargue los archivos CSV de Marzo 2026 para generar el consolidado en Excel e Informe Word.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Fallas Internas")
    file_fallas = st.file_uploader("Subir CSV Internas", type=['csv'], key="fallas")

with col2:
    st.subheader("2. Reporte ISP")
    file_isp = st.file_uploader("Subir CSV ISP", type=['csv'], key="isp")

with col3:
    st.subheader("3. Reclamos")
    file_reclamos = st.file_uploader("Subir CSV Reclamos", type=['csv'], key="reclamos")

# PROCESAR SI ESTÁN CARGADOS
if file_fallas and file_isp and file_reclamos:
    # Definir palabras clave para encontrar encabezados
    df_f = clean_meru_csv(file_fallas, ["FECHA", "TIPO DE FALLA", "DURACIÓN"])
    df_i = clean_meru_csv(file_isp, ["NOMBRE ISP", "TIPO DE FALLA", "RESPUESTA ISP"])
    df_r = clean_meru_csv(file_reclamos, ["ABONADO", "TIPO DE RECLAMO", "SOLUCIÓN"])

    if df_f is not None and df_i is not None and df_r is not None:
        st.success("✅ Archivos procesados correctamente.")
        
        # --- VISTA PREVIA ---
        with st.expander("Ver Datos Procesados"):
            t1, t2, t3 = st.tabs(["Fallas Internas", "Reporte ISP", "Reclamos"])
            t1.dataframe(df_f.head())
            t2.dataframe(df_i.head())
            t3.dataframe(df_r.head())

        st.markdown("---")
        st.subheader("📥 Descargar Entregables")
        
        d_col1, d_col2 = st.columns(2)
        
        # Generar Excel
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            df_f.to_excel(writer, sheet_name='Fallas Internas', index=False)
            df_i.to_excel(writer, sheet_name='Reporte ISP', index=False)
            df_r.to_excel(writer, sheet_name='Reclamos Abonados', index=False)
        
        d_col1.download_button(
            label="📊 Descargar Excel Consolidado",
            data=output_excel.getvalue(),
            file_name="CONSOLIDADO_MARZO_2026_MERU.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Generar Word
        word_buffer = generate_word_report(df_f, df_i, df_r)
        d_col2.download_button(
            label="📝 Descargar Informe Word (DOCX)",
            data=word_buffer,
            file_name="INFORME_GESTION_MARZO_2026_MERU.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # --- WHATSAPP PREVIEW ---
        st.markdown("---")
        st.subheader("📲 Resumen para WhatsApp")
        whatsapp_text = f"""*REPORTE NOC MERU - MARZO 2026* 📡

✅ *Fallas Internas:* {len(df_f)} eventos atendidos.
🌐 *Fallas ISP:* {len(df_i)} eventos reportados.
🎫 *Gestión Abonados:* {len(df_r)} reclamos gestionados.

_Informe generado automáticamente por el Sistema de Gestión Meru_"""
        st.code(whatsapp_text, language=None)

else:
    st.warning("Esperando la carga de los 3 archivos para habilitar las descargas.")
