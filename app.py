import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="NOC Meru-Networks", layout="wide")
st.title("🛰️ Sistema de Gestión NOC - Meru-Networks")

# 1. Subida de archivos desde la Web
st.sidebar.header("Carga de Datos de Marzo")
archivos = st.sidebar.file_uploader("Arrastra aquí tus 5 o 6 archivos", accept_multiple_files=True)

if archivos:
    datos = {f.name: f for f in archivos}
    
    # Buscador inteligente por palabras clave
    uso_f = next((v for k,v in datos.items() if 'Usage' in k), None)
    ebno_f = next((v for k,v in datos.items() if 'statistics (42)' in k), None)
    isp_f = next((v for k,v in datos.items() if 'ISP' in k), None)

    if uso_f and ebno_f:
        # Procesamiento
        df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
        df_ebno = pd.read_csv(ebno_f, sep=None, engine='python')
        
        # Dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Nodos (GB)")
            # (Aquí va el código de la gráfica de barras que ya definimos)
            
        with col2:
            st.subheader("Calidad Eb/No vs Tráfico")
            # (Aquí va el gráfico de dispersión)
            
        st.success("✅ Análisis de Marzo completado con éxito.")
