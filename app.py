import streamlit as st
import streamlit.components.v1 as components

# 1. Configuración de la página (Ancho completo y título en la pestaña)
st.set_page_config(
    page_title="Meru Networks - Executive Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inyectar CSS para quitar los márgenes por defecto de Streamlit
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Tu código HTML Premium (El que diseñamos anteriormente)
# Nota: He pegado el código aquí dentro de una variable multilínea
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; margin: 0; }
        .glass-panel { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(226, 232, 240, 0.8); }
        .sidebar-link { transition: all 0.2s ease; cursor: pointer; }
        .sidebar-link:hover { background: rgba(59, 130, 246, 0.1); color: #2563eb; }
        .active-link { background: #2563eb; color: white !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body class="flex h-screen overflow-hidden">
    <!-- Aquí va todo el contenido del <body> que generamos en el paso anterior -->
    <!-- (Por brevedad, asegúrate de que el contenido del body sea el mismo del artefacto anterior) -->
    
    <aside class="w-64 glass-panel h-full flex flex-col p-6 z-20 shadow-xl">
        <div class="mb-10 flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">M</div>
            <h1 class="text-lg font-bold text-slate-800 tracking-tight">MERU <span class="text-blue-600">NOC</span></h1>
        </div>
        <nav class="space-y-1 flex-grow">
            <div onclick="parent.window.location.reload()" class="sidebar-link active-link flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold">Dashboard</div>
            <div class="sidebar-link text-slate-600 flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold">Gestión</div>
        </nav>
    </aside>

    <main class="flex-grow p-8 overflow-y-auto bg-slate-50">
        <header class="mb-8">
            <h2 class="text-3xl font-black text-slate-900">Resumen Ejecutivo</h2>
            <p class="text-slate-500">Visualización de datos Meru Networks</p>
        </header>
        
        <div class="grid grid-cols-3 gap-6 mb-8">
            <div class="glass-panel p-6 rounded-2xl">
                <p class="text-xs font-bold text-slate-400 uppercase">Tráfico Total</p>
                <h4 class="text-2xl font-black">1.2 TB</h4>
            </div>
            <div class="glass-panel p-6 rounded-2xl">
                <p class="text-xs font-bold text-slate-400 uppercase">Uptime</p>
                <h4 class="text-2xl font-black">99.9%</h4>
            </div>
            <div class="glass-panel p-6 rounded-2xl">
                <p class="text-xs font-bold text-slate-400 uppercase">Eb/No</p>
                <h4 class="text-2xl font-black text-blue-600">14.2</h4>
            </div>
        </div>

        <div class="glass-panel p-8 rounded-[2rem] h-96">
             <canvas id="chartStreamlit"></canvas>
        </div>
    </main>

    <script>
        const ctx = document.getElementById('chartStreamlit').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['01', '05', '10', '15', '20', '25', '30'],
                datasets: [{
                    label: 'Rendimiento Eb/No',
                    data: [12, 14, 13.5, 15, 14.2, 14.8, 14.2],
                    borderColor: '#2563eb',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(37, 99, 235, 0.05)'
                }]
            },
            options: { maintainAspectRatio: false }
        });
    </script>
</body>
</html>
"""

# 4. Renderizar el HTML a pantalla completa
components.html(html_code, height=1000, scrolling=True)
