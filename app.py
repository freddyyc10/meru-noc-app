import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="MERU NOC - Dashboard",
    page_icon="📡",
    layout="wide"
)

def render_noc_status(nodes_data):
    """
    Renderiza un panel de control estilo NOC usando React.
    Corregido el error de f-string mediante el escape de llaves.
    """
    json_data = json.dumps(nodes_data)

    # Nota: Usamos triple llave para las variables de JS que están dentro de un f-string
    # o simplemente construimos el string con cuidado.
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
    <body class="bg-slate-900 text-white font-sans">
        <div id="root"></div>
        <script type="text/babel">
            const {{ motion }} = FramerMotion;

            const NodeCard = ({{ node }}) => (
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-lg"
                >
                    <div className="flex justify-between items-center mb-3">
                        <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">{{node.id}}</span>
                        <div className="flex items-center gap-2">
                            <div className={`h-2.5 w-2.5 rounded-full ${{node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}}`}></div>
                        </div>
                    </div>
                    
                    <h3 className="text-lg font-bold text-slate-100 truncate">{{node.name}}</h3>
                    <div className="text-xs text-slate-500 font-mono mb-4">IP: {{node.ip}}</div>
                    
                    <div className="grid grid-cols-2 gap-2 text-center">
                        <div className="bg-slate-900/50 p-2 rounded border border-slate-700">
                            <div className="text-[10px] text-slate-500 uppercase">Latencia</div>
                            <div className="text-sm font-mono text-emerald-400 font-bold">{{node.latency}}ms</div>
                        </div>
                        <div className="bg-slate-900/50 p-2 rounded border border-slate-700">
                            <div className="text-[10px] text-slate-500 uppercase">Carga</div>
                            <div className="text-sm font-mono text-blue-400 font-bold">{{node.load}}%</div>
                        </div>
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
    return components.html(react_html, height=500, scrolling=True)

# --- LÓGICA DE PROCESAMIENTO ---

def main():
    st.title("📡 MERU NOC - Monitoreo de Estaciones")
    
    # Datos simulados (Aquí integrarías tu lógica de pandas)
    network_nodes = [
        {"id": "V-CCS-01", "name": "Hub Caracas Main", "ip": "10.0.0.1", "status": "online", "latency": 12, "load": 45},
        {"id": "V-MRU-02", "name": "Remote Meru South", "ip": "10.0.0.5", "status": "online", "latency": 580, "load": 22},
        {"id": "V-BCK-03", "name": "Backup Gateway", "ip": "172.16.1.1", "status": "offline", "latency": 0, "load": 0},
    ]

    st.subheader("Estado de Nodos (React/Tailwind Component)")
    render_noc_status(network_nodes)

if __name__ == "__main__":
    main()
