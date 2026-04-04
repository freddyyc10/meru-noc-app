import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de la página (Debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Meru NOC Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_dashboard():
    # Buscamos el archivo index.html en el mismo directorio que app.py
    path_to_html = "index.html"
    
    if os.path.exists(path_to_html):
        try:
            with open(path_to_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Estilos para que el dashboard ocupe toda la pantalla disponible en Streamlit
            st.markdown("""
                <style>
                    /* Ocultar el header y footer de Streamlit */
                    header {visibility: hidden;}
                    footer {visibility: hidden;}
                    #MainMenu {visibility: hidden;}
                    
                    /* Eliminar paddings de la aplicación */
                    .main .block-container {
                        padding: 0rem;
                        max-width: 100%;
                    }
                    
                    /* Quitar bordes del iframe */
                    iframe {
                        border: none;
                        width: 100%;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Renderizamos el HTML
            # Ajustamos la altura a 100vh o un valor fijo grande para evitar scroll doble
            components.html(html_content, height=1200, scrolling=True)
            
        except Exception as e:
            st.error(f"Error al leer el archivo HTML: {e}")
    else:
        st.error(f"⚠️ No se encontró el archivo '{path_to_html}'.")
        st.info("Asegúrate de que el archivo index.html esté en la raíz de tu repositorio junto a app.py.")

if __name__ == "__main__":
    load_dashboard()
