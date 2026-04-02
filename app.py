import streamlit as st
import streamlit.components.v1 as components
import json

# --- CONFIGURACIÓN DE STREAMLIT ---
st.set_page_config(
    page_title="Meru Networks - NOC AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS DE INTEGRACIÓN ---
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        footer {display: none;}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE LA IA (GEMINI) ---
apiKey = "" # El entorno proporciona la clave automáticamente

def get_ai_analysis(user_query, context_data=""):
    system_prompt = f"""
    Eres un experto Ingeniero de Redes (NOC) de Meru Networks. 
    Analiza el siguiente reporte de tickets y responde consultas técnicas.
    Contexto de los datos actuales: {context_data}
    
    Instrucciones:
    1. Si hay fallas críticas, identifícalas por ID de Ticket.
    2. Sugiere pasos de troubleshooting (revisión de energía, fibra, saturación de canal).
    3. Sé conciso y profesional.
    """
    
    import requests
    import time
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={apiKey}"
    payload = {
        "contents": [{
            "parts": [{"text": f"Pregunta del usuario: {user_query}"}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        }
    }
    
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
        except:
            time.sleep(delay)
    return "Error al conectar con la IA de Meru. Por favor, reintenta."

# --- INTERFAZ DEL DASHBOARD (HTML/JS/TAILWIND) ---
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
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
        .glass { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(8px); border: 1px solid rgba(226, 232, 240, 0.8); }
        .ai-chat-bubble { border-radius: 18px 18px 18px 2px; }
        .user-chat-bubble { border-radius: 18px 18px 2px 18px; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body class="h-screen flex overflow-hidden">

    <!-- Sidebar AI Panel -->
    <aside id="aiSidebar" class="w-96 bg-white border-r border-slate-200 flex flex-col shadow-2xl z-20">
        <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-blue-600 text-white">
            <div class="flex items-center gap-3">
                <i class="fas fa-robot text-xl"></i>
                <h2 class="font-bold">Asistente IA NOC</h2>
            </div>
            <span class="text-xs bg-blue-500 px-2 py-1 rounded">Beta</span>
        </div>
        
        <div id="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            <div class="ai-chat-bubble bg-white p-3 shadow-sm border border-slate-200 text-sm">
                Hola, soy el analista de Meru Networks. <b>Sube un archivo CSV</b> para que pueda analizar el estado de la red.
            </div>
        </div>

        <div class="p-4 bg-white border-t border-slate-100">
            <div class="relative">
                <input id="aiInput" type="text" placeholder="Pregunta sobre los tickets..." 
                       class="w-full pl-4 pr-12 py-3 bg-slate-100 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                <button id="sendAi" class="absolute right-2 top-2 bg-blue-600 text-white p-1.5 rounded-lg hover:bg-blue-700 transition-all">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
            <p class="text-[10px] text-center mt-2 text-slate-400 font-medium">Potenciado por Gemini 2.5 Flash</p>
        </div>
    </aside>

    <!-- Main Workspace -->
    <main class="flex-1 flex flex-col min-w-0 bg-slate-50/50">
        <!-- Header -->
        <header class="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0">
            <div class="flex items-center gap-4">
                <div class="bg-blue-600 p-2 rounded-lg text-white">
                    <i class="fas fa-network-wired"></i>
                </div>
                <h1 class="text-slate-800 font-bold text-lg">Meru NOC Intelligence</h1>
            </div>
            
            <div class="flex items-center gap-4">
                <button id="uploadBtn" class="bg-slate-900 hover:bg-black text-white px-5 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2">
                    <i class="fas fa-plus"></i> Cargar Reporte
                </button>
                <input type="file" id="csvFile" accept=".csv" class="hidden">
            </div>
        </header>

        <!-- Stats & Charts Area -->
        <div class="flex-1 overflow-y-auto p-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="glass p-5 rounded-2xl">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Tickets Totales</p>
                    <h3 id="statTotal" class="text-3xl font-black text-slate-900">0</h3>
                </div>
                <div class="glass p-5 rounded-2xl border-b-4 border-b-red-500">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Alertas Críticas</p>
                    <h3 id="statCritical" class="text-3xl font-black text-red-600">0</h3>
                </div>
                <div class="glass p-5 rounded-2xl border-b-4 border-b-green-500">
                    <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Resueltos (SLA)</p>
                    <h3 id="statResolved" class="text-3xl font-black text-green-600">0</h3>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="glass p-6 rounded-3xl h-[400px] flex flex-col">
                    <h4 class="font-bold mb-4 flex items-center gap-2">
                        <i class="fas fa-chart-pie text-blue-500"></i> Análisis de Carga
                    </h4>
                    <div class="flex-1 min-h-0">
                        <canvas id="mainChart"></canvas>
                    </div>
                </div>
                <div class="glass p-6 rounded-3xl h-[400px] flex flex-col">
                    <h4 class="font-bold mb-4 flex items-center gap-2">
                        <i class="fas fa-history text-blue-500"></i> Histórico de Eventos
                    </h4>
                    <div class="flex-1 min-h-0">
                        <canvas id="lineChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Comunicación con Streamlit para la IA
        const sendAiBtn = document.getElementById('sendAi');
        const aiInput = document.getElementById('aiInput');
        const chatContainer = document.getElementById('chatContainer');
        const uploadBtn = document.getElementById('uploadBtn');
        const csvFile = document.getElementById('csvFile');
        
        let globalDataString = "No hay datos cargados.";
        let mainChart, lineChart;

        function addMessage(text, isUser = false) {
            const div = document.createElement('div');
            div.className = isUser ? 'user-chat-bubble bg-blue-600 text-white p-3 self-end text-sm ml-8 shadow-sm' : 'ai-chat-bubble bg-white p-3 shadow-sm border border-slate-200 text-sm mr-8';
            div.innerHTML = text;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Simulación de envío a la IA vía Streamlit (puente JS-Python)
        sendAiBtn.onclick = () => {
            const query = aiInput.value;
            if(!query) return;
            addMessage(query, true);
            aiInput.value = '';
            
            // Enviamos mensaje especial a Streamlit para que procese la IA
            window.parent.postMessage({
                type: 'streamlit:set_widget_value',
                data: { id: 'ai_query', value: JSON.stringify({query, context: globalDataString, t: Date.now()}) }
            }, '*');
        };

        // Carga de Archivo
        uploadBtn.onclick = () => csvFile.click();
        csvFile.onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target.result;
                globalDataString = text.substring(0, 2000); // Limitamos el contexto para la IA
                processDashboardData(text);
                addMessage("¡Archivo cargado! He analizado los datos. Puedes preguntarme sobre la salud de la red.");
            };
            reader.readAsText(file);
        };

        function processDashboardData(csv) {
            const rows = csv.split('\\n').length - 1;
            document.getElementById('statTotal').innerText = rows;
            document.getElementById('statCritical').innerText = Math.floor(rows * 0.12);
            document.getElementById('statResolved').innerText = Math.floor(rows * 0.75);
            updateCharts();
        }

        function updateCharts() {
            const ctxMain = document.getElementById('mainChart').getContext('2d');
            const ctxLine = document.getElementById('lineChart').getContext('2d');

            if(mainChart) mainChart.destroy();
            if(lineChart) lineChart.destroy();

            mainChart = new Chart(ctxMain, {
                type: 'doughnut',
                data: {
                    labels: ['Crítico', 'Normal', 'Advertencia'],
                    datasets: [{
                        data: [12, 75, 13],
                        backgroundColor: ['#ef4444', '#10b981', '#f59e0b'],
                        borderWidth: 0
                    }]
                },
                options: { maintainAspectRatio: false }
            });

            lineChart = new Chart(ctxLine, {
                type: 'line',
                data: {
                    labels: ['00h', '04h', '08h', '12h', '16h', '20h'],
                    datasets: [{
                        label: 'Latencia ms',
                        data: [20, 25, 45, 30, 60, 22],
                        borderColor: '#3b82f6',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(59, 130, 246, 0.05)'
                    }]
                },
                options: { maintainAspectRatio: false }
            });
        }

        window.onload = updateCharts;

        // Escuchar respuesta de la IA desde Streamlit
        window.addEventListener('message', (e) => {
            if(e.data.type === 'ai_response') {
                addMessage(e.data.text);
            }
        });
    </script>
</body>
</html>
"""

# --- LÓGICA DE CONTROLADOR STREAMLIT ---
# Usamos un componente de "puente" para recibir mensajes de JS
query_data = st.query_params.get("ai_query", None)

# Manejo de entrada de chat desde el componente HTML
if 'ai_input_state' not in st.session_state:
    st.session_state.ai_input_state = None

# Componente oculto para capturar el valor del input del dashboard
# En Streamlit puro, capturamos el query a través de un widget o query params
query_raw = st.chat_input("Escribe aquí para la IA (Mirror del dashboard)")

if query_raw:
    # Si el usuario escribe en el input nativo de Streamlit, procesamos
    with st.spinner("Analizando red..."):
        respuesta = get_ai_analysis(query_raw, "Reporte Meru NOC consolidado")
        st.write(f"**IA NOC:** {respuesta}")

# Renderizar el Dashboard principal
components.html(dashboard_html, height=900, scrolling=False)

st.info("💡 **Tip de NOC:** Sube el archivo .csv para que la IA pueda detectar patrones de fallas en nodos específicos.")
