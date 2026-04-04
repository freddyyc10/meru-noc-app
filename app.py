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
    Se eliminó el f-string para evitar errores de sintaxis con las llaves de JS.
    """
    # Convertimos los datos de Python a un string JSON seguro
    json_data = json.dumps(nodes_data)

    # Definimos el HTML como un string plano (sin f-string)
    # Usamos un placeholder TEMPLATE_DATA para inyectar los datos después
    react_html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>
    </head>
    <body class="bg-slate-900 text-white font-sans">
        <div id="root"></div>
        <script type="text/babel">
            const { motion } = FramerMotion;

            const NodeCard = ({ node }) => (
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800 border border-slate-700 p-4 rounded-xl shadow-lg hover:border-blue-500/50 transition-colors"
                >
                    <div className="flex justify-between items-center mb-3">
                        <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest">{node.id}</span>
                        <div className="flex items-center gap-2">
                            <div className={`h-2.5 w-2.5 rounded-full ${node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-rose-500 shadow-[0_0_10px_#f43f5e]'}`}></div>
                            <span className="text-[10px] uppercase font-bold text-slate-400">{node.status}</span>
                        </div>
                    </div>
                    
                    <h3 className="text-lg font-bold text-slate-100 truncate">{node.name}</h3>
                    <div className="text-xs text-slate-500 font-mono mb-4">IP: {node.ip}</div>
                    
                    <div className="grid grid-cols-2 gap-2 text-center">
                        <div className="bg-slate-900/50 p-2 rounded border border-slate-700">
                            <div className="text-[10px] text-slate-500 uppercase">Latencia</div>
                            <div className="text-sm font-mono text-emerald-400 font-bold">{node.latency}ms</div>
                        </div>
                        <div className="bg-slate-900/50 p-2 rounded border border-slate-700">
                            <div className="text-[10px] text-slate-500 uppercase">Carga</div>
                            <div className="text-sm font-mono text-blue-400 font-bold">{node.load}%</div>
                        </div>
                    </div>
                </motion.div>
            );

            const App = () => {
                const nodes = TEMPLATE_DATA;
                return (
                    <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {nodes.map((node, i) => (
                            <NodeCard key={i} node={node} />
                        ))}
                    </div>
                );
            };

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    
    # Inyectamos los datos reemplazando el placeholder
    final_html = react_html_template.replace("TEMPLATE_DATA", json_data)
    
    return components.html(final_html, height=600, scrolling=True)

def main():
    st.title("📡 MERU NOC - Monitoreo en Tiempo Real")
    
    # Datos de ejemplo (puedes cargarlos desde tu CSV)
    network_nodes = [
        {"id": "V-CCS-01", "name": "Hub Caracas Main", "ip": "10.0.0.1", "status": "online", "latency": 12, "load": 45},
        {"id": "V-MRU-02", "name": "Remote Meru South", "ip": "10.0.0.5", "status": "online", "latency": 580, "load": 22},
        {"id": "V-BCK-03", "name": "Backup Gateway", "ip": "172.16.1.1", "status": "offline", "latency": 0, "load": 0},
        {"id": "V-VAL-04", "name": "Valencia Node", "ip": "10.0.2.10", "status": "online", "latency": 25, "load": 88},
    ]

    st.write("Estado de las estaciones:")
    render_noc_status(network_nodes)

if __name__ == "__main__":
    main()
