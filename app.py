import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="NOC Meru-Networks", layout="wide")
st.title("🛰️ Sistema de Gestión NOC - Meru-Networks")

# Barra lateral para carga
with st.sidebar:
    st.header("📂 Carga de Datos")
    archivos = st.file_uploader("Sube tus archivos CSV/XLSX aquí", accept_multiple_files=True)

if archivos:
    # Diccionario de archivos subidos
    docs = {f.name: f for f in archivos}
    st.info(f"Archivos cargados: {', '.join(docs.keys())}")

    # --- PROCESAMIENTO DE TRÁFICO (El archivo que ya subiste) ---
    uso_f = next((v for k,v in docs.items() if 'Usage' in k or 'VNO' in k), None)
    
    if uso_f:
        try:
            df_uso = pd.read_csv(uso_f, skiprows=3, sep=None, engine='python')
            cols_in = [c for c in df_uso.columns if ' In' in c]
            
            resumen = []
            for c in cols_in:
                n = c.replace(' In', '')
                total = (df_uso[c].sum() + df_uso[n+' Out'].sum()) / 1024
                resumen.append({'Nodo': n, 'GB': round(total, 2)})
            
            df_rank = pd.DataFrame(resumen).sort_values('GB', ascending=False)

            # --- VISUALIZACIÓN ---
            st.subheader("📊 Reporte de Consumo Mensual (Marzo 2026)")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(data=df_rank.head(12), x='GB', y='Nodo', palette='viridis')
                st.pyplot(fig)
            
            with col2:
                st.write("**Top Nodos Críticos**")
                st.dataframe(df_rank.head(10))

        except Exception as e:
            st.error(f"Error al leer el archivo de tráfico: {e}")
    else:
        st.warning("⚠️ Sube el archivo de 'Usage Report' para ver las gráficas de tráfico.")

    # --- PROCESAMIENTO DE EB/NO ---
    ebno_f = next((v for k,v in docs.items() if 'statistics' in k), None)
    if ebno_f:
        st.success("✅ Datos de Eb/No detectados. Procesando calidad de señal...")
        # Aquí se activaría el gráfico de dispersión automáticamente
else:
    st.write("👋 **Bienvenido.** Por favor, arrastra los archivos de marzo a la izquierda para generar el reporte.")
