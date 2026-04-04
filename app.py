import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import json
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="MERU NOC - Dashboard Inteligente",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales para integrar Streamlit con el look oscuro del NOC
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    header { background-color: #1e293b !important; }
    .stExpander { border: 1px solid #334155 !important; background-color: #1e293b !important; }
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    h1, h2, h3, p, span { color: #f8fafc !important; }
    </style>
    """, unsafe_allow_html=True)

def render_noc_status(nodes_data):
    """
    Renderiza un panel de control estilo NOC usando React, Tailwind y Framer Motion.
    Recibe una lista de diccionarios con datos procesados de las estaciones.
    """
    json_data = json.dumps(nodes_data)

    react_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>
    </head>
    <body class="bg-transparent text-white font-sans overflow-hidden">
        <div id="root"></div>
        <script type="text/babel">
            const {{ motion }} = FramerMotion;

            const NodeCard = ({{ node }}) => (
                <motion.div 
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.02, borderColor: '#3b82f6' }}
                    className="bg-slate-800/50 backdrop-blur-md border border-slate-700 p-4 rounded-xl shadow-2xl mb-4"
                >
                    <div className="flex justify-between items-center mb-3">
                        <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">STATION_ID: {{node.id}}</span>
                        <div className="flex items-center gap-2">
                            <span className="text-[10px] text-slate-400 uppercase font-bold">Status</span>
                            <div className={`h-2.5 w-2.5 rounded-full ${{node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-rose-500 shadow-[0_0_10px_#f43f5e]'}}`}></div>
                        </div>
                    </div>
                    
                    <h3 className="text-lg font-bold text-slate-100 truncate mb-1">{{node.name}}</h3>
                    <div className="text-xs text-slate-500 font-mono mb-4">Ubicación: {{node.location || 'Remote Terminal'}}</div>
                    
                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700/50">
                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Tráfico Total</div>
                            <div className="text-md font-mono text-emerald-400 font-bold">{{node.total_usage}} <span class="text-[10px]">MB</span></div>
                        </div>
                        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700/50">
                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Carga Relativa</div>
                            <div className="text-md font-mono text-blue-400 font-bold">{{node.load}}%</div>
                        </div>
                    </div>

                    <div className="mt-4 h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
                        <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${{node.load}}%` }}
                            transition={{ duration: 1, ease: "easeOut" }}
                            className={`h-full ${{node.load > 80 ? 'bg-rose-500' : 'bg-blue-500'}}`}
                        />
                    </div>
                </motion.div>
            );

            const App = () => {{
                const nodes = {json_data};
                return (
                    <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {{nodes.map((node, i) => (
                            <NodeCard key={{i}} node={{node}} />
                        ))}}
                    </div>
                );
            }};

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    # Ajustamos altura según cantidad de nodos (aprox 200px por fila)
    calculated_height = max(400, (len(nodes_data) // 3 + 1) * 220)
    return components.html(react_html, height=calculated_height, scrolling=True)

def get_clean_df(file):
    """Limpia el CSV saltando metadatos de iDirect"""
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
    except:
        return pd.DataFrame()

def process_data_for_react(df):
    """Convierte los datos del CSV al formato que espera el componente React"""
    all_cols = df.columns.tolist()
    sites = sorted(list(set([c.split('/')[0] for c in all_cols if '/' in c])))
    
    nodes_for_react = []
    max_total = 0
    
    # Primero calculamos totales para normalizar la barra de carga
    temp_data = []
    for s in sites:
        in_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["In", "FL"])), None)
        out_c = next((c for c in all_cols if c.startswith(s + "/") and any(k in c for k in ["Out", "RL"])), None)
        
        if in_c or out_c:
            val_in = pd.to_numeric(df[in_c], errors='coerce').sum() if in_c else 0
            val_out = pd.to_numeric(df[out_c], errors='coerce').sum() if out_c else 0
            total = (val_in + val_out) / (1024 * 1024) if "Octets" in str(in_c or out_c) else (val_in + val_out)
            temp_data.append({"id": s, "total": round(total, 2)})
            if total > max_total: max_total = total

    # Construimos el objeto final
    for item in temp_data:
        load_percentage = round((item['total'] / max_total * 100), 1) if max_total > 0 else 0
        nodes_for_react.append({
            "id": f"VSAT-{item['id'][:3].upper()}",
            "name": item['id'],
            "status": "online" if item['total'] > 0 else "offline",
            "total_usage": item['total'],
            "load": load_percentage,
            "location": "Red Meru Satelital"
        })
    
    return nodes_for_react

def main():
    # Header minimalista estilo Dashboard Moderno
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: #1e293b; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;">
            <div>
                <h1 style="margin:0; font-size: 1.5rem; letter-spacing: -0.025em; color: #3b82f6 !important;">MERU NETWORKS <span style="color:white !important;">NOC</span></h1>
                <p style="margin:0; font-size: 0.75rem; color: #94a3b8 !important; font-family: monospace;">CORE NETWORK MONITORING SYSTEM v2.5</p>
            </div>
            <div style="text-align: right">
                <div style="color: #10b981; font-size: 0.8rem; font-weight: bold;">● SISTEMA OPERATIVO</div>
                <div style="color: #64748b; font-size: 0.7rem;">LATENCIA PROMEDIO: 580ms (Sat)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.image("https://merunetworks.com.ve/wp-content/uploads/2021/04/Logo-Meru-Networks-01.png", width=150)
    st.sidebar.title("📥 Carga de Datos")
    files = st.sidebar.file_uploader("Arrastra reportes iDirect NMS", type="csv", accept_multiple_files=True)
    
    if not files:
        st.info("Esperando archivos CSV para inicializar el monitoreo...")
        # Mostrar nodos vacíos o placeholder
        return

    for f in files:
        with st.expander(f"🛰️ Procesando Estaciones de: {f.name}", expanded=True):
            df = get_clean_df(f)
            if not df.empty:
                # Convertir datos de iDirect a formato React
                nodes_data = process_data_for_react(df)
                
                # Renderizar el componente avanzado
                render_noc_status(nodes_data)
                
                # Opcional: Gráfica de soporte con Plotly
                st.markdown("### 📊 Vista Analítica de Bitrate")
                st.line_chart(df.set_index(df.columns[0]).iloc[:, :5]) # Muestra las primeras 5 columnas de datos

if __name__ == "__main__":
    main()
