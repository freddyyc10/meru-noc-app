import streamlit as st
import streamlit.components.v1 as components
import json

# Configuración estética de Streamlit para el NOC
st.set_page_config(page_title="MERU NOC - Dashboard", layout="wide", initial_sidebar_state="expanded")

def render_noc_status(nodes_data):
    """
    Renderiza un panel de control estilo NOC usando React, Tailwind y Framer Motion.
    """
    # Convertimos los datos de Python a JSON para React
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
        <!-- Lucide Icons -->
        <script src="https://unpkg.com/lucide@latest"></script>
    </head>
    <body class="bg-slate-900 text-white font-sans">
        <div id="root"></div>

        <script type="text/babel">
            const {{ useState, useEffect }} = React;
            const {{ motion, AnimatePresence }} = FramerMotion;

            const NodeCard = ({{ node }}) => (
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800 border border-slate-700 p-4 rounded-lg shadow-xl"
                >
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{{node.id}}</span>
                        <div className={`h-3 w-3 rounded-full ${{node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'}}`}></div>
                    </div>
                    <h3 className="text-lg font-bold mb-1">{{node.name}}</h3>
                    <div className="text-sm text-slate-400">IP: {{node.ip}}</div>
                    
                    <div className="mt-4 grid grid-cols-2 gap-2 text-center text-xs">
                        <div className="bg-slate-900 p-2 rounded">
                            <div className="text-slate-500 uppercase">Latencia</div>
                            <div className="font-mono text-emerald-400 font-bold">{{node.latency}}ms</div>
                        </div>
                        <div className="bg-slate-900 p-2 rounded">
                            <div className="text-slate-500 uppercase">Carga</div>
                            <div className="font-mono text-blue-400 font-bold">{{node.load}}%</div>
                        </div>
                    </div>
                </motion.div>
            );

            const App = () => {{
                const nodes = {json_data};
                
                return (
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {{nodes.map(node => (
                                <NodeCard key={{node.id}} node={{node}} />
                            ))}}
                        </div>
                    </div>
                );
            }};

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<App />);
        </script>
    </body>
    </html>
    """
    return components.html(react_html, height=600, scrolling=True)

# --- LÓGICA DE STREAMLIT ---

st.sidebar.title("🛠️ Configuración NOC")
st.sidebar.markdown("Panel de control para la red de **Meru**.")

# Datos de ejemplo (Esto vendría de tu base de datos o API)
network_nodes = [
    {{"id": "SRV-01", "name": "Core Router Caracas", "ip": "10.0.0.1", "status": "online", "latency": 12, "load": 45}},
    {{"id": "SRV-02", "name": "Edge Switch Meru", "ip": "10.0.0.5", "status": "online", "latency": 8, "load": 22}},
    {{"id": "SRV-03", "name": "Backup Gateway", "ip": "192.168.1.1", "status": "offline", "latency": 0, "load": 0}},
    {{"id": "SRV-04", "name": "Dist-Switch-04", "ip": "10.0.2.10", "status": "online", "latency": 15, "load": 78}},
]

# Título y renderizado
st.subheader("🌐 Monitoreo de Nodos en Tiempo Real (React Component)")
render_noc_status(network_nodes)

st.write("---")
st.caption("Sistema de Monitoreo Meru-NOC v1.0")
