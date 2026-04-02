mport React, { useState, useEffect } from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import { 
  LayoutDashboard, Search, Server, Activity, ShieldCheck, 
  RefreshCw, ChevronRight, Settings, Download, FileUp, 
  FileText, CheckCircle2, XCircle, BrainCircuit, Bell,
  Menu, User, LogOut, Zap
} from 'lucide-react';

const apiKey = "";

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [aiReport, setAiReport] = useState(null);

  // Datos de los Nodos de Meru
  const nodes = [
    { id: 'ND-001', name: 'Nodo Norte - Caracas', status: 'online', latency: '12ms', load: '45%' },
    { id: 'ND-002', name: 'Nodo Centro - Maracay', status: 'online', latency: '18ms', load: '62%' },
    { id: 'ND-003', name: 'Nodo Sur - Bolívar', status: 'warning', latency: '85ms', load: '88%' },
    { id: 'ND-004', name: 'Nodo Occidente - Zulia', status: 'offline', latency: '0ms', load: '0%' },
  ];

  const chartData = [
    { name: '00:00', traffic: 400 },
    { name: '04:00', traffic: 300 },
    { name: '08:00', traffic: 800 },
    { name: '12:00', traffic: 750 },
    { name: '16:00', traffic: 600 },
    { name: '20:00', traffic: 450 },
  ];

  const generateAIReport = async (csvData) => {
    setLoading(true);
    const systemPrompt = "Eres el analista senior del NOC de Meru. Analiza los datos CSV y genera un informe de salud de red.";
    const userQuery = `Analiza estos datos de red: ${csvData}`;

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: userQuery }] }],
          systemInstruction: { parts: [{ text: systemPrompt }] }
        })
      });

      const result = await response.json();
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
      setAiReport(text || "No se pudo generar el análisis.");
    } catch (err) {
      setAiReport("Error al conectar con la IA. Verifique la conexión.");
    } finally {
      setLoading(false);
    }
  };

  const handleImportCSV = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          generateAIReport(event.target.result.substring(0, 3000));
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  return (
    <div className="flex min-h-screen bg-[#f8fafc] font-sans text-[#1e293b]">
      {/* Sidebar - Menú Original Preservado */}
      <aside className="w-64 bg-[#1e293b] text-white fixed h-full flex flex-col shadow-xl">
        <div className="p-6 border-b border-slate-700 flex items-center gap-3">
          <div className="bg-blue-500 p-2 rounded-lg">
            <Zap size={20} className="fill-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">Meru NOC</span>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <p className="text-[10px] font-bold text-slate-500 uppercase px-4 mb-2">Principal</p>
          <button onClick={() => setActiveTab('dashboard')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'dashboard' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:bg-slate-800'}`}>
            <LayoutDashboard size={18} /> Dashboard
          </button>
          <button onClick={() => setActiveTab('nodos')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'nodos' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:bg-slate-800'}`}>
            <Activity size={18} /> Nodos de Red
          </button>
          
          <p className="text-[10px] font-bold text-slate-500 uppercase px-4 mt-6 mb-2">Herramientas</p>
          <button onClick={() => setActiveTab('search')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'search' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:bg-slate-800'}`}>
            <BrainCircuit size={18} /> Meru AI Expert
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 transition-all">
            <Settings size={18} /> Configuración
          </button>
        </nav>

        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center gap-3 px-4 py-3 bg-slate-800 rounded-2xl">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold">AD</div>
            <div className="flex-1 overflow-hidden">
              <p className="text-xs font-bold truncate">Admin Meru</p>
              <p className="text-[10px] text-slate-500 truncate">Online</p>
            </div>
            <LogOut size={14} className="text-slate-500 cursor-pointer hover:text-white" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 p-8">
        <header className="flex justify-between items-center mb-8 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight">CENTRAL DE OPERACIONES</h1>
            <p className="text-slate-400 text-xs font-medium uppercase tracking-widest">Infraestructura Crítica Meru</p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Bell size={20} className="text-slate-400 mt-2 mr-4" />
              <span className="absolute top-1 right-4 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </div>
            <button onClick={handleImportCSV} className="flex items-center gap-2 bg-[#f1f5f9] px-4 py-2.5 rounded-xl text-xs font-bold hover:bg-slate-200 transition-all">
              <FileUp size={14} /> IMPORTAR LOGS
            </button>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {loading && (
              <div className="bg-blue-600 p-6 rounded-3xl text-white flex items-center justify-between shadow-lg shadow-blue-100">
                <div className="flex items-center gap-4">
                  <RefreshCw size={24} className="animate-spin" />
                  <div>
                    <p className="font-bold">Analizando Tráfico en Tiempo Real</p>
                    <p className="text-blue-100 text-xs">La IA está procesando los paquetes de red...</p>
                  </div>
                </div>
              </div>
            )}

            {aiReport && (
              <div className="bg-white p-8 rounded-3xl border-l-4 border-l-blue-600 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <div className="bg-blue-100 p-2 rounded-lg text-blue-600">
                    <BrainCircuit size={18} />
                  </div>
                  <h3 className="font-black text-sm uppercase tracking-wider">Reporte Predictivo IA</h3>
                </div>
                <div className="text-slate-600 text-sm leading-relaxed whitespace-pre-line bg-slate-50 p-6 rounded-2xl border border-slate-100">
                  {aiReport}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
                <div className="flex justify-between items-center mb-8">
                  <h3 className="font-black text-sm uppercase tracking-widest flex items-center gap-2">
                    <Activity size={16} className="text-blue-600" /> Rendimiento de Red
                  </h3>
                  <select className="text-xs font-bold bg-slate-50 border-none rounded-lg px-3 py-1 text-slate-500">
                    <option>Últimas 24 horas</option>
                  </select>
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="colorTraffic" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8'}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8'}} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                      />
                      <Area type="monotone" dataKey="traffic" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTraffic)" strokeWidth={4} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-6">
                <div className="bg-[#1e293b] p-8 rounded-3xl text-white shadow-xl relative overflow-hidden">
                  <div className="relative z-10">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Status Global</p>
                    <p className="text-4xl font-black mb-2">99.98%</p>
                    <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                      <CheckCircle2 size={12} /> Operativo
                    </div>
                  </div>
                  <Activity size={80} className="absolute -bottom-4 -right-4 text-slate-800 opacity-50" />
                </div>
                <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Nodos Activos</p>
                  <p className="text-4xl font-black text-slate-800">12/14</p>
                  <div className="mt-4 w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div className="bg-blue-600 h-full w-[85%] rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'nodos' && (
          <div className="grid grid-cols-1 gap-4">
            <div className="flex items-center justify-between mb-4 px-2">
              <h2 className="font-black text-slate-800 uppercase tracking-tight">Inventario de Nodos</h2>
              <div className="flex gap-2">
                <div className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-lg text-[10px] font-bold uppercase">Online: 12</div>
                <div className="bg-rose-100 text-rose-700 px-3 py-1 rounded-lg text-[10px] font-bold uppercase">Critical: 2</div>
              </div>
            </div>
            {nodes.map(node => (
              <div key={node.id} className="bg-white p-6 rounded-3xl border border-slate-200 flex items-center justify-between hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group shadow-sm">
                <div className="flex items-center gap-6">
                  {/* CORRECCIÓN DE SINTAXIS AQUÍ */}
                  <div className={`p-5 rounded-2xl ${
                    node.status === 'online' ? 'bg-emerald-50 text-emerald-600' : 
                    node.status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600'
                  }`}>
                    <Server size={24} />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg text-slate-800 group-hover:text-blue-600 transition-colors">{node.name}</h4>
                    <p className="text-xs font-mono text-slate-400 bg-slate-50 px-2 py-0.5 rounded inline-block mt-1">{node.id}</p>
                  </div>
                </div>
                <div className="flex gap-12 items-center mr-4">
                  <div className="text-right">
                    <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Ping</p>
                    <p className="font-black text-slate-700">{node.latency}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Load</p>
                    <p className="font-black text-slate-700">{node.load}</p>
                  </div>
                  <div className={`w-32 py-2 rounded-xl text-center text-[10px] font-black uppercase tracking-widest shadow-sm ${
                    node.status === 'online' ? 'bg-emerald-500 text-white shadow-emerald-100' : 
                    node.status === 'warning' ? 'bg-amber-500 text-white shadow-amber-100' : 'bg-rose-500 text-white shadow-rose-100'
                  }`}>
                    {node.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'search' && (
          <div className="max-w-3xl mx-auto text-center py-20 bg-white rounded-[40px] border border-slate-200 shadow-sm px-10 mt-10">
            <div className="bg-blue-600 w-20 h-20 rounded-[30px] flex items-center justify-center text-white mx-auto mb-8 shadow-2xl shadow-blue-200">
              <BrainCircuit size={40} />
            </div>
            <h2 className="text-4xl font-black text-slate-800 mb-4 tracking-tight">MERU AI CONSULTANT</h2>
            <p className="text-slate-500 mb-10 max-w-md mx-auto text-sm leading-relaxed">
              Interactúa con el modelo Gemini 2.5 para diagnosticar problemas de red o planificar expansiones de nodos.
            </p>
            <div className="relative group">
              <input 
                type="text" 
                placeholder="Escribe tu consulta técnica..." 
                className="w-full p-6 pl-8 pr-40 rounded-3xl border-2 border-slate-100 shadow-sm focus:border-blue-500 focus:outline-none transition-all text-sm font-medium"
              />
              <button className="absolute right-3 top-3 bottom-3 bg-blue-600 text-white px-8 rounded-2xl font-bold text-xs uppercase tracking-widest hover:bg-blue-700 transition-all">
                Enviar
              </button>
            </div>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {['Análisis de Tráfico', 'Check Salud Nodo Sur', 'Optimizar Rutas'].map(tag => (
                <span key={tag} className="bg-slate-50 text-slate-500 px-4 py-2 rounded-full text-[10px] font-bold border border-slate-100 cursor-pointer hover:bg-slate-100">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
