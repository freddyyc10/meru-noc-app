import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
import io
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Dashboard",
    page_icon="📡",
    layout="wide"
)

# --- CONFIGURACIÓN DE API GEMINI ---
apiKey = "" # La plataforma inyectará el key automáticamente

def call_gemini_analysis(data_summary):
    """Llamada a Gemini para analizar los datos del NOC"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    
    prompt = f"""
    Eres un experto en redes satelitales iDirect. Analiza el siguiente resumen de tráfico y estado de estaciones:
    {data_summary}
    
    Proporciona:
    1. Identificación de anomalías (estaciones con tráfico inusual o caídas).
    2. Recomendaciones técnicas para optimizar el ancho de banda.
    3. Un resumen ejecutivo para la gerencia de Meru Networks.
    Responde en español de forma profesional.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        # Implementación simple de reintento/backoff no incluida para brevedad pero recomendada
        response = requests.post(url, json=payload)
        result = response.json()
        return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "No se pudo generar el análisis.")
    except Exception as e:
        return f"Error conectando con la IA: {str(e)}"

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    div[data-testid="stExpander"] { border: 1px solid #334155; background-color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

def get_clean_df(file):
    content = file.getvalue().decode('utf-8', errors='ignore').splitlines()
    skip_rows = 0
    for i, line in enumerate(content):
        if any(key in line for key in ["Date", "Time", "Octets", "Bit Rate", "Eb/No"]):
            skip_rows = i
            break
    file.seek(0)
    try:
        df = pd.read_csv(file, skiprows=skip_rows)
        df.columns = [str(c).strip().replace('"', '') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

def render_react_noc(nodes_data):
    """Renderiza el panel visual estilo NOC sin errores de llaves"""
    json_data = json.dumps(nodes_data)
    
    # Usamos constantes de JS para evitar conflictos con llaves de Python
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-[#0f172a]">
        <div id="root"></div>
        <script type="text/babel">
            const NodeCard = ({ node }) => (
                <div class="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-lg m-2">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-mono text-blue-400">ID: {node.id}</span>
                        <div class={`h-3 w-3 rounded-full ${node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500'}`}></div>
                    </div>
                    <h3 class="text-white font-bold truncate">{node.name}</h3>
                    <div class="grid grid-cols-2 gap-2 mt-3">
                        <div class="bg-slate-900 p-2 rounded text-center">
                            <div class="text-[9px] text-slate-500 uppercase">Carga</div>
                            <div class="text-sm font-mono text-emerald-400">{node.load}%</div>
                        </div>
                        <div class="bg-slate-900 p-2 rounded text-center">
                            <div class="text-[9px] text-slate-500 uppercase">Tráfico</div>
                            <div class="text-sm font-mono text-blue-400">{node.traffic}</div>
                        </div>
                    </div>
                </div>
            );

            const App = () => {
                const nodes = DATA_PLACEHOLDER;
                return (
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
                        {nodes.map((n, i) => <NodeCard key={i} node={n} />)}
                    </div>
                );
            };

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """.replace("DATA_PLACEHOLDER", json_data)
    
    components.html(html_content, height=450, scrolling=True)

def main():
    # --- LOGO Y CABECERA ---
    col1, col2 = st.columns([1, 3])
    with col1:
        # Usamos la ruta local que mencionaste en GitHub
        try:
            st.image("Meru Networks JPG Horizontal.jpg", width=300)
        except:
            st.markdown("### MERU NETWORKS")

    with col2:
        st.title("Sistema de Monitoreo NOC v2.5")
        st.write("Visualización Inteligente y Análisis de Telemetría")

    # --- BARRA LATERAL ---
    st.sidebar.title("Configuración")
    files = st.sidebar.file_uploader("Subir reportes CSV de iDirect", type="csv", accept_multiple_files=True)

    if not files:
        st.info("💡 Suba archivos CSV de estadísticas para activar el análisis.")
        return

    for f in files:
        with st.expander(f"📊 Análisis: {f.name}", expanded=True):
            df = get_clean_df(f)
            if df.empty: continue
            
            all_cols = df.columns.tolist()
            cols_text = " ".join(all_cols).lower()

            # Lógica para reportes de consumo
            if any(k in cols_text for k in ["octets", "bit rate"]):
                sites = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
                nodes_for_ui = []
                summary_text = ""

                for s in sites:
                    in_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
                    out_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
                    
                    val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
                    val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
                    total = val_in + val_out
                    
                    nodes_for_ui.append({
                        "id": s[:5],
                        "name": s,
                        "status": "online" if total > 0 else "offline",
                        "load": round((val_in / (total + 1)) * 100, 1) if total > 0 else 0,
                        "traffic": f"{round(total/1024/1024, 2)}MB" if "Octets" in str(in_c) else f"{round(total, 0)}bps"
                    })
                    summary_text += f"Estación {s}: In={val_in}, Out={val_out}. "

                # Mostrar Interfaz React
                render_react_noc(nodes_for_ui)

                # --- BOTÓN DE IA CON GEMINI ---
                st.divider()
                st.subheader("🤖 Consultoría con IA (Gemini)")
                if st.button(f"Analizar tendencias de {f.name} con Gemini", key=f"btn_{f.name}"):
                    with st.spinner("Gemini está analizando los patrones de red..."):
                        analisis = call_gemini_analysis(summary_text[:2000]) # Límite de texto para seguridad
                        st.markdown(f"**Análisis de la IA:**\n\n{analisis}")
                
                # Gráfico complementario
                fig = px.pie(pd.DataFrame(nodes_for_ui), values='load', names='name', title="Distribución de Carga")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)

            else:
                # Reporte de señal (Eb/No)
                st.subheader("📈 Niveles de Señal (Eb/No / Power)")
                stations = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
                selected = st.selectbox("Estación:", stations, key=f"sig_{f.name}")
                if selected:
                    plot_cols = [c for c in all_cols if c.startswith(selected + "/")]
                    fig = px.line(df, y=plot_cols, title=f"Histórico: {selected}")
                    fig.update_layout(template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
