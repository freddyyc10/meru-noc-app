import streamlit as st
import streamlit.components.v1 as components

# Configuración de la interfaz de Streamlit
st.set_page_config(
    page_title="Meru Networks - NOC Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS para limpiar la interfaz de Streamlit y que el Dashboard sea el protagonista
st.markdown("""
    <style>
        /* Eliminar paddings y márgenes por defecto de Streamlit */
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        footer {display: none;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Ajustar el iframe para que sea responsivo */
        iframe {
            border: none;
            width: 100%;
            height: 100vh;
        }
    </style>
""", unsafe_allow_html=True)

# El contenido HTML/JS/CSS consolidado en una sola variable
dashboard_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .glass-card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(226, 232, 240, 0.8); }
        .sidebar-item:hover { background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; }
        .sidebar-active { background-color: rgba(59, 130, 246, 0.15); border-left: 4px solid #2563eb; color: #2563eb; }
    </style>
</head>
<body class="overflow-hidden">
    <div class="flex h-screen overflow-hidden">
        <!-- Sidebar -->
        <aside class="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col">
            <div class="p-6 border-b border-slate-100 flex items-center gap-3">
                <div class="bg-blue-600 p-2 rounded-lg text-white">
                    <i class="fas fa-satellite-dish"></i>
                </div>
                <h1 class="font-bold text-xl text-slate-800">Meru NOC</h1>
            </div>
            
            <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
                <div class="sidebar-active sidebar-item p-3 rounded-lg flex items-center gap-3 cursor-pointer transition-all">
                    <i class="fas fa-chart-line"></i>
                    <span class="font-medium">Resumen General</span>
                </div>
                <div class="sidebar-item p-3 rounded-lg flex items-center gap-3 text-slate-600 cursor-pointer transition-all">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Tickets Críticos</span>
                </div>
                <div class="sidebar-item p-3 rounded-lg flex items-center gap-3 text-slate-600 cursor-pointer transition-all">
                    <i class="fas fa-history"></i>
                    <span>Histórico de Fallas</span>
                </div>
                <div class="sidebar-item p-3 rounded-lg flex items-center gap-3 text-slate-600 cursor-pointer transition-all">
                    <i class="fas fa-file-export"></i>
                    <span>Exportar Reportes</span>
                </div>
            </nav>
            
            <div class="p-4 border-t border-slate-100">
                <div class="bg-slate-50 p-4 rounded-xl">
                    <p class="text-xs text-slate-500 mb-1 font-semibold uppercase">Estado del Sistema</p>
                    <div class="flex items-center gap-2">
                        <span class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                        <span class="text-sm font-medium text-slate-700">Online y Sincronizado</span>
                    </div>
                </div>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 flex flex-col min-w-0 overflow-hidden">
            <!-- Header -->
            <header class="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="md:hidden bg-blue-600 p-2 rounded text-white cursor-pointer">
                        <i class="fas fa-bars"></i>
                    </div>
                    <h2 class="text-slate-800 font-semibold text-lg">Suite Ejecutiva de Reportes</h2>
                </div>
                
                <div class="flex items-center gap-4">
                    <div class="hidden sm:flex items-center bg-slate-100 rounded-lg px-3 py-1.5 border border-slate-200">
                        <i class="fas fa-calendar-alt text-slate-400 text-sm mr-2"></i>
                        <span id="currentDate" class="text-sm font-medium text-slate-600"></span>
                    </div>
                    <button id="uploadBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-lg shadow-blue-200 flex items-center gap-2">
                        <i class="fas fa-upload"></i>
                        Cargar CSV
                    </button>
                    <input type="file" id="csvFile" accept=".csv" class="hidden">
                </div>
            </header>

            <!-- Dashboard Content -->
            <div id="dashboardContent" class="flex-1 p-8 overflow-y-auto bg-slate-50/50">
                <!-- Welcome Section -->
                <div class="mb-8">
                    <h3 class="text-2xl font-bold text-slate-800">Bienvenido al Centro de Control Meru</h3>
                    <p class="text-slate-500">Cargue el reporte consolidado de tickets para visualizar las métricas clave del NOC.</p>
                </div>

                <!-- Stats Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div class="bg-blue-50 text-blue-600 p-3 rounded-xl">
                                <i class="fas fa-ticket-alt text-xl"></i>
                            </div>
                        </div>
                        <p class="text-slate-500 text-sm font-medium">Total Tickets</p>
                        <h4 id="statTotal" class="text-3xl font-bold text-slate-900">--</h4>
                    </div>
                    <div class="glass-card p-6 rounded-2xl shadow-sm border-l-4 border-l-red-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="bg-red-50 text-red-600 p-3 rounded-xl">
                                <i class="fas fa-clock text-xl"></i>
                            </div>
                        </div>
                        <p class="text-slate-500 text-sm font-medium">Fuera de SLA</p>
                        <h4 id="statSla" class="text-3xl font-bold text-slate-900">--</h4>
                    </div>
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div class="bg-green-50 text-green-600 p-3 rounded-xl">
                                <i class="fas fa-check-circle text-xl"></i>
                            </div>
                        </div>
                        <p class="text-slate-500 text-sm font-medium">Resueltos Hoy</p>
                        <h4 id="statResolved" class="text-3xl font-bold text-slate-900">--</h4>
                    </div>
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <div class="bg-amber-50 text-amber-600 p-3 rounded-xl">
                                <i class="fas fa-tools text-xl"></i>
                            </div>
                        </div>
                        <p class="text-slate-500 text-sm font-medium">En Progreso</p>
                        <h4 id="statPending" class="text-3xl font-bold text-slate-900">--</h4>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <div class="flex items-center justify-between mb-6">
                            <h5 class="font-bold text-slate-800">Distribución por Severidad</h5>
                            <button class="text-blue-600 text-xs font-semibold hover:underline">Ver detalles</button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="severityChart"></canvas>
                        </div>
                    </div>
                    <div class="glass-card p-6 rounded-2xl shadow-sm">
                        <div class="flex items-center justify-between mb-6">
                            <h5 class="font-bold text-slate-800">Tendencia Semanal de Fallas</h5>
                            <button class="text-blue-600 text-xs font-semibold hover:underline">Filtrar</button>
                        </div>
                        <div class="relative h-64">
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity / Table -->
                <div class="glass-card rounded-2xl shadow-sm overflow-hidden">
                    <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-white">
                        <h5 class="font-bold text-slate-800">Registros Procesados Recientemente</h5>
                        <div class="flex gap-2">
                            <input type="text" placeholder="Buscar ticket..." class="text-sm px-3 py-1.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20">
                        </div>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider">
                                    <th class="px-6 py-4">ID Ticket</th>
                                    <th class="px-6 py-4">Cliente / Nodo</th>
                                    <th class="px-6 py-4">Estado</th>
                                    <th class="px-6 py-4">SLA</th>
                                    <th class="px-6 py-4 text-right">Acción</th>
                                </tr>
                            </thead>
                            <tbody id="tableBody" class="divide-y divide-slate-100 text-sm text-slate-600">
                                <tr>
                                    <td colspan="5" class="px-6 py-8 text-center text-slate-400 italic">No hay datos cargados para mostrar</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Set Today's Date
        document.getElementById('currentDate').innerText = new Date().toLocaleDateString('es-ES', { 
            day: 'numeric', month: 'long', year: 'numeric' 
        });

        const uploadBtn = document.getElementById('uploadBtn');
        const csvFileInput = document.getElementById('csvFile');
        let severityChart, trendChart;

        uploadBtn.addEventListener('click', () => csvFileInput.click());

        csvFileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(event) {
                const text = event.target.result;
                processCSV(text);
            };
            reader.readAsText(file);
        });

        function processCSV(csvText) {
            const rows = csvText.split('\\n').map(row => row.split(','));
            const headers = rows[0];
            const data = rows.slice(1).filter(row => row.length > 1);

            // Simulación de procesamiento (Debes adaptar esto a tus columnas reales)
            const stats = {
                total: data.length,
                sla: Math.floor(data.length * 0.15), // Ejemplo: 15% fuera de SLA
                resolved: Math.floor(data.length * 0.4),
                pending: Math.floor(data.length * 0.45)
            };

            // Update UI Stats
            document.getElementById('statTotal').innerText = stats.total;
            document.getElementById('statSla').innerText = stats.sla;
            document.getElementById('statResolved').innerText = stats.resolved;
            document.getElementById('statPending').innerText = stats.pending;

            updateCharts();
            updateTable(data.slice(0, 5)); // Mostrar primeros 5
        }

        function updateCharts() {
            const ctxSeverity = document.getElementById('severityChart').getContext('2d');
            const ctxTrend = document.getElementById('trendChart').getContext('2d');

            if(severityChart) severityChart.destroy();
            if(trendChart) trendChart.destroy();

            severityChart = new Chart(ctxSeverity, {
                type: 'doughnut',
                data: {
                    labels: ['Crítico', 'Alto', 'Medio', 'Bajo'],
                    datasets: [{
                        data: [12, 19, 3, 5],
                        backgroundColor: ['#ef4444', '#f97316', '#3b82f6', '#10b981'],
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'right' } },
                    cutout: '70%'
                }
            });

            trendChart = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
                    datasets: [{
                        label: 'Tickets Abiertos',
                        data: [65, 59, 80, 81, 56, 55, 40],
                        fill: true,
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderColor: '#3b82f6',
                        tension: 0.4
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true }, x: { grid: { display: false } } }
                }
            });
        }

        function updateTable(sampleData) {
            const tableBody = document.getElementById('tableBody');
            tableBody.innerHTML = '';
            
            sampleData.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-6 py-4 font-semibold text-slate-700">#${1000 + index}</td>
                    <td class="px-6 py-4">
                        <div class="flex flex-col">
                            <span class="font-medium text-slate-800">${row[0] || 'Cliente Desconocido'}</span>
                            <span class="text-xs text-slate-400">Nodo Principal</span>
                        </div>
                    </td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-600">Pendiente</span>
                    </td>
                    <td class="px-6 py-4">
                        <div class="w-24 bg-slate-200 rounded-full h-1.5">
                            <div class="bg-blue-600 h-1.5 rounded-full" style="width: 75%"></div>
                        </div>
                    </td>
                    <td class="px-6 py-4 text-right">
                        <button class="text-slate-400 hover:text-blue-600 transition-colors"><i class="fas fa-ellipsis-v"></i></button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }

        // Initialize with empty charts
        window.onload = updateCharts;
    </script>
</body>
</html>
"""

# Renderizar el componente
# Ajustamos la altura a 1000px para evitar scrollbars dobles en resoluciones comunes
components.html(dashboard_html, height=1000, scrolling=True)
