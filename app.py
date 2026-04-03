import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Meru NOC Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_dashboard():
    # Buscamos el archivo index.html en el mismo directorio
    path_to_html = "index.html"
    
    if os.path.exists(path_to_html):
        with open(path_to_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Renderizamos el HTML dentro de Streamlit
        # Usamos una altura grande (1200px) o ajustable para que se vea el dashboard completo
        components.html(html_content, height=1200, scrolling=True)
    else:
        st.error(f"No se encontró el archivo {path_to_html}. Asegúrate de que esté en la misma carpeta que app.py")

if __name__ == "__main__":
    # Eliminamos márgenes por defecto de Streamlit para que el dashboard luzca mejor
    st.markdown("""
        <style>
            .main .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            iframe {
                border-radius: 15px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    load_dashboard()
