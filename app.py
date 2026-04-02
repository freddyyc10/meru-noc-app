import streamlit as st
import streamlit.components.v1 as components

# 1. Configuración de la página para que ocupe todo el ancho
st.set_page_config(
    page_title="Meru Networks | NOC Executive",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inyección de CSS para eliminar los márgenes blancos de Streamlit y forzar el fondo oscuro
st.markdown("""
    <style>
        /* Eliminar padding del contenedor principal */
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        /* Ocultar elementos innecesarios de Streamlit */
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        /* Forzar fondo oscuro en la carga */
        body, .stApp {
            background-color: #0f172a;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Tu código HTML modificado y optimizado para el componente
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Inter', sans-serif; 
            background-color: #0f172a; 
            color: #f1f5f9;
            margin: 0;
            overflow-x: hidden;
        }
        .glass { 
            background: rgba(30, 41, 59, 0.7); 
            backdrop-filter: blur(16px); 
            border: 1px solid rgba(255, 255, 255, 0.05); 
        }
        .sidebar-item { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .sidebar-item:hover { background: rgba(59, 130, 246, 0.1); transform: translateX(4px); }
        .active-nav { background: linear-gradient(90deg, #2563eb 0%, transparent 100%); border-left: 4px solid #3b82f6; }
        .stat-card { transition: transform 0.3s ease; }
        .stat-card:hover { transform: translateY(-5px); border-color: rgba(59, 130, 246, 0.4); }
        .meru-table th { color: #94a3b8; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; padding: 1rem; }
        .meru-table td { padding: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade { animation: fadeIn 0.5s ease forwards; }
    </style>
</head>
<body class="flex min-h-screen">

    <!-- Sidebar -->
    <aside class="w-80 glass border-r border-slate-800 flex flex-col p-8 z-30 hidden md:flex">
        <div class="mb-12">
            <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                </div>
                <h1 class="text-2xl font-black tracking-tighter italic">MERU<span class="text-blue-500">NET</span></h1>
            </div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-[0.3em]">Operational Intelligence</p>
        </div>

        <nav class="space-y-2 flex-grow">
            <button onclick="showPage('dash')" id="nav-dash" class="sidebar-item active-nav w-full flex items-center gap-4 px-4 py-3 rounded-r-xl text-sm font-semibold text-white">
                Dashboard
            </button>
            <button onclick="showPage('upload')" id="nav-upload" class="sidebar-item w-full flex items-center gap-4 px-4 py-3 rounded-r-xl text-sm font-semibold text-slate-400">
                Carga Mensual
            </button>
            <button onclick="showPage('tickets')" id="nav-tickets" class="sidebar-item w-full flex items-center gap-4 px-4 py-3 rounded-r-xl text-sm font-semibold text-slate-400">
                Tickets NOC
            </button>
        </nav>
    </aside>

    <!-- Main View -->
    <main class="flex-grow relative h-screen overflow-y-auto px-6 md:px-12 py-10">
        <header class="flex flex-col md:flex-row justify-between items-start mb-12 animate-fade">
            <div>
                <h2 id="page-title" class="text-4xl font-extrabold text-white tracking-tight mb-2">Dashboard Ejecutivo</h2>
                <p id="page-subtitle" class="text-slate-400 text-sm">Vista general de rendimiento de red satelital.</p>
            </div>
            <div class="mt-4 md:mt-0 flex items-center gap-4">
                <div class="flex flex-col items-end mr-4">
                    <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Periodo Actual</span>
                    <span id="header-period" class="text-sm font-bold text-blue-400">Marzo 2026</span>
                </div>
            </div>
        </header>

        <!-- Contenido dinámico -->
        <div id="page-dash" class="space-y-8 animate-fade">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="glass p-6 rounded-3xl stat-card border-l-4 border-l-blue-500">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Throughput Promedio</p>
                    <h3 class="text-3xl font-black text-white">842 <span class="text-sm font-normal text-slate-400">Mbps</span></h3>
                </div>
                <div class="glass p-6 rounded-3xl stat-card border-l-4 border-l-purple-500">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Disponibilidad</p>
                    <h3 class="text-3xl font-black text-white">99.92 <span class="text-sm font-normal text-slate-400">%</span></h3>
                </div>
                <div class="glass p-6 rounded-3xl stat-card border-l-4 border-l-orange-500">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Señal Promedio</p>
                    <h3 class="text-3xl font-black text-white">12.8 <span class="text-sm font-normal text-slate-400">dB</span></h3>
                </div>
                <div class="glass p-6 rounded-3xl stat-card border-l-4 border-l-red-500">
                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2">Incidencias</p>
                    <h3 class="text-3xl font-black text-white">02</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="glass p-8 rounded-[2.5rem]">
                    <h4 class="font-bold text-slate-200 mb-6">Consumo de Tráfico por Nodo</h4>
                    <canvas id="trafficChart" height="250"></canvas>
                </div>
                <div class="glass p-8 rounded-[2.5rem]">
                    <h4 class="font-bold text-slate-200 mb-6">Distribución de Errores RF</h4>
                    <canvas id="signalChart" height="250"></canvas>
                </div>
            </div>
        </div>

        <!-- Secciones Ocultas Inicialmente -->
        <div id="page-upload" class="hidden animate-fade">
             <div class="glass p-12 rounded-[3rem] text-center">
                <h3 class="text-xl font-bold">Módulo de Carga</h3>
                <p class="text-slate-400 mt-2">Arrastra tus archivos CSV aquí</p>
             </div>
        </div>

        <div id="page-tickets" class="hidden animate-fade text-white">
             <div class="glass rounded-[2rem] overflow-hidden">
                <table class="w-full meru-table">
                    <thead><tr class="bg-slate-800"><th>Folio</th><th>Nodo</th><th>Estatus</th></tr></thead>
                    <tbody>
                        <tr><td class="text-blue-400">#TK-0042</td><td>MIR68_PAPARO</td><td>SLA OK</td></tr>
                    </tbody>
                </table>
             </div>
        </div>

    </main>

    <script>
        function showPage(id) {
            ['dash', 'upload', 'tickets'].forEach(p => {
                document.getElementById('page-' + p).classList.add('hidden');
                document.getElementById('nav-' + p)?.classList.remove('active-nav', 'text-white');
            });
            document.getElementById('page-' + id).classList.remove('hidden');
            document.getElementById('nav-' + id)?.classList.add('active-nav', 'text-white');
        }

        window.onload = () => {
            const chartConfig = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            };

            new Chart(document.getElementById('trafficChart'), {
                type: 'bar',
                data: {
                    labels: ['ZUL36', 'MIR68', 'GUA19', 'AMA05', 'DC72'],
                    datasets: [{
                        data: [450, 380, 320, 290, 610],
                        backgroundColor: '#3b82f6',
                        borderRadius: 8
                    }]
                },
                options: chartConfig
            });

            new Chart(document.getElementById('signalChart'), {
                type: 'line',
                data: {
                    labels: ['01', '05', '10', '15', '20', '25', '30'],
                    datasets: [{
                        data: [12.1, 11.8, 12.5, 10.2, 12.9, 13.1, 12.8],
                        borderColor: '#a855f7',
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 2
                    }]
                },
                options: chartConfig
            });
        };
    </script>
</body>
</html>
"""

# 4. Renderizado Final
# Usamos un alto de 1000px para que el dashboard sea cómodo
components.html(html_content, height=1000, scrolling=True)
