import streamlit as st
import pandas as pd
import io

def cargar_datos_seguro(uploaded_file):
    """
    Intenta cargar un archivo manejando errores de delimitadores y formato.
    """
    if uploaded_file is None:
        return None

    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    
    try:
        # 1. Si es Excel, Pandas suele manejarlo bien directamente
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            return pd.read_excel(uploaded_file)

        # 2. Si es CSV, leemos el contenido para detectar el separador
        content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        
        # Intentamos detectar separadores comunes
        # Si la línea 1 tiene muchos ';', el separador es ';'
        first_line = content.split('\n')[0]
        sep = ','
        if ';' in first_line and first_line.count(';') > first_line.count(','):
            sep = ';'
        elif '\t' in first_line:
            sep = '\t'

        # 3. Intentamos la carga con el separador detectado
        # on_bad_lines='skip' evita que el programa se rompa si hay líneas corruptas
        df = pd.read_csv(
            io.StringIO(content), 
            sep=sep, 
            on_bad_lines='skip', 
            engine='python'
        )
        
        if df.empty:
            st.error("El archivo parece estar vacío o no tiene columnas válidas.")
            return None
            
        return df

    except Exception as e:
        st.error(f"Error crítico al procesar: {e}")
        return None

# --- Interfaz de Streamlit ---
st.title("Procesador de Archivos NOC")

archivo = st.file_uploader("Sube tu archivo de datos (CSV o Excel)", type=["csv", "xlsx"])

if archivo:
    df = cargar_datos_seguro(archivo)
    
    if df is not None:
        st.success(f"Archivo cargado con éxito: {len(df)} filas detectadas.")
        st.write("### Vista Previa de los Datos")
        st.dataframe(df.head(10))
        
        # Mostrar columnas para asegurar que se detectaron bien
        st.write("### Columnas Detectadas")
        st.write(list(df.columns))
    else:
        st.warning("No se pudieron extraer datos. Revisa si el archivo tiene un formato extraño.")
