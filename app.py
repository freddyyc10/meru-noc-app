<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meru Networks NOC</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            overflow-x: hidden;
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            transition: all 0.3s ease;
        }

        .glass-card:hover {
            border: 1px solid rgba(59, 130, 246, 0.5);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);
        }

        .meru-gradient {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        }

        .status-dot {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px currentColor;
        }
    </style>
</head>
<body class="p-6">

    <!-- Header / Navbar -->
    <header class="flex justify-between items-center mb-8 px-4">
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 meru-gradient rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
                <i class="fas fa-broadcast-tower text-white text-xl"></i>
            </div>
            <div>
                <h1 class="text-2xl font-bold tracking-tight text-white">MERU <span class="text-blue-400">NETWORKS</span></h1>
                <p class="text-slate-400 text-xs font-medium uppercase tracking-widest">Global NOC Operations</p>
            </div>
        </div>

        <div class="flex gap-4">
            <div class="glass-card px-4 py-2 flex items-center gap-3">
                <span class="status-dot text-emerald-400 bg-emerald-400"></span>
                <span class="text-sm font-semibold">Sistema Online</span>
            </div>
            <button class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-bold transition-all flex items-center gap-2">
                <i class="fas fa-file-export"></i> Exportar Reporte
            </button>
        </div>
    </header>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <!-- KPI 1 -->
        <div class="glass-card p-6">
            <div class="flex justify-between items-start mb-4">
                <p class="text-slate-400 text-sm font-medium">Sitios Totales</p>
                <i class="fas fa-network-wired text-blue-400"></i>
            </div>
            <h3 class="text-3xl font-bold">1,248</h3>
            <p class="text-emerald-400 text-xs mt-2 font-bold"><i class="fas fa-arrow-up"></i> +12% esta semana</p>
        </div>

        <!-- KPI 2 -->
        <div class="glass-card p-6">
            <div class="flex justify-between items-start mb-4">
                <p class="text-slate-400 text-sm font-medium">Tráfico Promedio</p>
                <i class="fas fa-chart-line text-purple-400"></i>
            </div>
            <h3 class="text-3xl font-bold">42.5 TB</h3>
            <p class="text-slate-400 text-xs mt-2 font-medium">Consumo mensual</p>
        </div>

        <!-- KPI 3 -->
        <div class="glass-card p-6">
            <div class="flex justify-between items-start mb-4">
                <p class="text-slate-400 text-sm font-medium">Disponibilidad</p>
                <i class="fas fa-check-circle text-emerald-400"></i>
            </div>
            <h3 class="text-3xl font-bold text-emerald-400">99.9%</h3>
            <p class="text-slate-400 text-xs mt-2 font-medium">SLA Objetivo</p>
        </div>

        <!-- KPI 4 -->
        <div class="glass-card p-6 border-l-4 border-red-500">
            <div class="flex justify-between items-start mb-4">
                <p class="text-slate-400 text-sm font-medium">Alertas NOC</p>
                <i class="fas fa-exclamation-triangle text-red-500"></i>
            </div>
            <h3 class="text-3xl font-bold">03</h3>
            <p class="text-red-400 text-xs mt-2 font-bold underline cursor-pointer">Ver tickets críticos</p>
        </div>
    </div>

    <!-- Charts and Data -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Grafica Principal -->
        <div class="lg:col-span-2 glass-card p-6">
            <div class="flex justify-between items-center mb-6">
                <h4 class="font-bold text-lg">Histórico de Conectividad (7 días)</h4>
                <div class="flex gap-2">
                    <span class="px-3 py-1 bg-blue-500/10 text-blue-400 rounded text-xs font-bold uppercase">Activos</span>
                    <span class="px-3 py-1 bg-slate-700 text-slate-400 rounded text-xs font-bold uppercase">Inactivos</span>
                </div>
            </div>
            <div class="h-64 flex items-center justify-center">
                <canvas id="mainChart"></canvas>
            </div>
        </div>

        <!-- Panel de Carga de Archivos (UI Mejorada) -->
        <div class="glass-card p-6">
            <h4 class="font-bold text-lg mb-4 flex items-center gap-2">
                <i class="fas fa-cloud-upload-alt text-blue-400"></i> Carga de Archivos
            </h4>
            <div class="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-blue-500 transition-all group cursor-pointer">
                <i class="fas fa-file-csv text-4xl text-slate-500 group-hover:text-blue-400 mb-4 transition-colors"></i>
                <p class="text-slate-300 font-medium">Arrastra tus archivos CSV aquí</p>
                <p class="text-slate-500 text-xs mt-1">Límite: 20MB por archivo</p>
            </div>

            <div class="mt-6 space-y-4">
                <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div class="flex items-center gap-3">
                        <i class="far fa-file-alt text-blue-400"></i>
                        <span class="text-sm font-medium text-slate-200">sitios_meru_oct.csv</span>
                    </div>
                    <span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded font-bold">LISTO</span>
                </div>
                <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div class="flex items-center gap-3">
                        <i class="far fa-file-alt text-blue-400"></i>
                        <span class="text-sm font-medium text-slate-200">trafico_nodos.csv</span>
                    </div>
                    <span class="text-[10px] bg-amber-500/20 text-amber-400 px-2 py-1 rounded font-bold">PROCESANDO</span>
                </div>
            </div>
        </div>

    </div>

    <script>
        // Configuración de la Gráfica
        const ctx = document.getElementById('mainChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
                datasets: [{
                    label: 'Conectividad %',
                    data: [98, 99, 97, 100, 99.5, 99.8, 99.9],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    </script>
</body>
</html>
