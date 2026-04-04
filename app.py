import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="NOC Meru Networks - Dashboard",
    page_icon="📡",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    [data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

def get_clean_df(file):
    """Limpia el CSV saltando metadatos de iDirect hasta encontrar la cabecera"""
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
    """
    Renderiza el panel visual estilo NOC.
    Se usa un string normal y .replace para evitar errores de llaves en f-strings de Python.
    """
    json_data = json.dumps(nodes_data)
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>
    </head>
    <body class="bg-[#0f172a] text-white">
        <div id="root"></div>
        <script type="text/babel">
            const { motion } = FramerMotion;

            const NodeCard = ({ node }) => (
                <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-slate-800/50 border border-slate-700 p-4 rounded-xl shadow-xl"
                >
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-[10px] font-mono text-blue-400">{node.id}</span>
                        <div class="flex items-center gap-2">
                            <div class={`h-2.5 w-2.5 rounded-full ${node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}`}></div>
                            <span class="text-[10px] uppercase font-bold text-slate-400">{node.status}</span>
                        </div>
                    </div>
                    <h3 class="text-md font-bold text-white truncate">{node.name}</h3>
                    <div class="text-[10px] text-slate-500 font-mono mb-3">IP: {node.ip}</div>
                    <div class="grid grid-cols-2 gap-2">
                        <div class="bg-slate-900/80 p-2 rounded border border-slate-700 text-center">
                            <div class="text-[9px] text-slate-500 uppercase">Latencia</div>
                            <div class="text-sm font-mono text-emerald-400">{node.latency}ms</div>
                        </div>
                        <div class="bg-slate-900/80 p-2 rounded border border-slate-700 text-center">
                            <div class="text-[9px] text-slate-500 uppercase">Carga</div>
                            <div class="text-sm font-mono text-blue-400">{node.load}%</div>
                        </div>
                    </div>
                </motion.div>
            );

            const App = () => {
                const nodes = DATA_PLACEHOLDER;
                return (
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-2">
                        {nodes.map((n, i) => <NodeCard key={i} node={n} />)}
                    </div>
                );
            };

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    final_html = html_template.replace("DATA_PLACEHOLDER", json_data)
    components.html(final_html, height=500, scrolling=True)

def main():
    # --- HEADER CON LOGO ---
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        # Nota: Usamos una URL de placeholder o el logo si estuviera accesible localmente
        st.image("https://raw.githubusercontent.com/fmarcano/meru-noc-app/main/logo.png", width=200, 
                 caption="Meru Networks", output_format="PNG")
    
    with col_title:
        st.title("📡 Sistema de Monitoreo NOC")
        st.write("Visualización de Telemetría y Consumo en Tiempo Real")

    # --- BARRA LATERAL ---
    st.sidebar.title("Configuración")
    files = st.sidebar.file_uploader("Subir reportes CSV", type="csv", accept_multiple_files=True)

    if not files:
        st.info("👋 Bienvenid@. Por favor, cargue archivos CSV en el panel lateral para comenzar.")
        
        # Dashboard vacío/ejemplo
        mock_nodes = [
            {"id": "GW-MAIN", "name": "Telepuerto Principal", "ip": "10.0.0.1", "status": "online", "latency": 15, "load": 42},
            {"id": "ST-001", "name": "Estación Sur", "ip": "10.0.5.12", "status": "online", "latency": 620, "load": 18},
            {"id": "ST-002", "name": "Estación Norte (Babel)", "ip": "10.0.5.13", "status": "offline", "latency": 0, "load": 0}
        ]
        st.subheader("Estado de Red (Demo)")
        render_react_noc(mock_nodes)
        return

    # --- PROCESAMIENTO DE ARCHIVOS ---
    for f in files:
        with st.expander(f"📁 Análisis de: {f.name}", expanded=True):
            df = get_clean_df(f)
            if df.empty: continue
            
            all_cols = df.columns.tolist()
            cols_text = " ".join(all_cols).lower()

            # Caso A: Reporte de Consumo (Octetos/Bits)
            if any(k in cols_text for k in ["octets", "bit rate", "fl bit", "rl bit"]):
                sites = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
                report_data = []
                
                for s in sites:
                    in_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
                    out_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
                    
                    if in_c or out_c:
                        val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
                        val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
                        is_bytes = "Octets" in str(in_c or out_c)
                        factor = (1024 * 1024) if is_bytes else 1
                        
                        report_data.append({
                            "id": s[:8],
                            "name": s,
                            "ip": "DHCP/Static",
                            "status": "online" if (val_in + val_out) > 0 else "offline",
                            "latency": int(df.iloc[-1].get('Latency', 0)) if 'Latency' in df.columns else 0,
                            "load": round((val_in / (val_in + val_out + 1)) * 100, 1) if (val_in + val_out) > 0 else 0
                        })

                # Mostrar visualización React
                render_react_noc(report_data)

                # Gráfico Plotly
                res_df = pd.DataFrame(report_data)
                fig = px.bar(res_df, x="name", y="load", title="Carga de Red por Estación",
                             color_discrete_sequence=['#3b82f6'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)

            # Caso B: Reporte de Señal (Eb/No, Power)
            else:
                st.subheader("📶 Histórico de Señal")
                stations = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
                selected = st.selectbox("Seleccione Estación:", stations, key=f"sel_{f.name}")
                
                if selected:
                    plot_cols = [c for c in all_cols if c.startswith(selected + "/")]
                    fig = go.Figure()
                    for c in plot_cols:
                        fig.add_trace(go.Scatter(x=df.index, y=df[c], name=c.split('/')[-1]))
                    
                    fig.update_layout(template="plotly_dark", title=f"Métricas: {selected}")
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
