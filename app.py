import React, { useState, useEffect } from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import { 
  LayoutDashboard, Search, Server, Activity, ShieldCheck, 
  RefreshCw, ChevronRight, Settings, Download, FileUp, 
  FileText, CheckCircle2, XCircle, BrainCircuit, Bell
} from 'lucide-react';

const apiKey = "";

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [aiReport, setAiReport] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

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
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 fixed h-full flex flex-col">
        <div className="p-6 border-b border-slate-100 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Server size={20} />
          </div>
          <span className="font-bold text-xl tracking-tight">Meru NOC</span>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          <button onClick={() => setActiveTab('dashboard')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'dashboard' ? 'bg-blue-50 text-blue-600 font-bold' : 'text-slate-500 hover:bg-slate-50'}`}>
            <LayoutDashboard size={20} /> Dashboard
          </button>
          <button onClick={() => setActiveTab('nodos')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'nodos' ? 'bg-blue-50 text-blue-600 font-bold' : 'text-slate-500 hover:bg-slate-50'}`}>
            <Activity size={20} /> Nodos
          </button>
          <button onClick={() => setActiveTab('search')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'search' ? 'bg-blue-50 text-blue-600 font-bold' : 'text-slate-500 hover:bg-slate-50'}`}>
            <BrainCircuit size={20} /> IA Expert
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 p-8">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-2xl font-bold text-slate-800 uppercase tracking-tight">Panel de Control</h1>
            <p className="text-slate-500 text-sm">Monitoreo de infraestructura Meru</p>
          </div>
          <div className="flex gap-3">
            <button onClick={handleImportCSV} className="flex items-center gap-2 bg-white border border-slate-200 px-4 py-2 rounded-xl text-sm font-bold shadow-sm hover:bg-slate-50 transition-all">
              <FileUp size={16} /> Importar CSV
            </button>
            <button className="bg-blue-600 text-white px-5 py-2 rounded-xl text-sm font-bold shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all">
              Live View
            </button>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {loading && (
              <div className="bg-blue-600 p-6 rounded-2xl text-white flex items-center gap-4 animate-pulse">
                <RefreshCw size={24} className="animate-spin" />
                <span className="font-bold">IA Meru analizando datos de red...</span>
              </div>
            )}

            {aiReport && (
              <div className="bg-white p-6 rounded-2xl border border-blue-100 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-blue-600">
                  <BrainCircuit size={20} />
                  <h3 className="font-bold uppercase text-xs tracking-widest">Análisis de Inteligencia</h3>
                </div>
                <div className="text-slate-700 text-sm leading-relaxed whitespace-pre-line font-medium">
                  {aiReport}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="font-bold mb-6 flex items-center gap-2">
                  <Activity size={18} className="text-blue-600" /> Tráfico de Red (Tbps)
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="colorTraffic" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8'}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8'}} />
                      <Tooltip />
                      <Area type="monotone" dataKey="traffic" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTraffic)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Uptime Global</p>
                  <p className="text-3xl font-black text-slate-800">99.98%</p>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Alertas Activas</p>
                  <p className="text-3xl font-black text-rose-600">02</p>
                </div>
                <div className="bg-slate-900 p-6 rounded-2xl shadow-xl shadow-slate-200 text-white">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">SLA Compromiso</p>
                  <p className="text-3xl font-black italic">MERU-S1</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'nodos' && (
          <div className="grid grid-cols-1 gap-4">
            {nodes.map(node => (
              <div key={node.id} className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center justify-between hover:border-blue-400 transition-all cursor-pointer group shadow-sm">
                <div className="flex items-center gap-4">
                  <div className={`p-4 rounded-xl ${
                    node.status === 'online' ? 'bg-emerald-50 text-emerald-600' : 
                    node.status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600'
                  }`}>
                    <Server size={20} />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">{node.name}</h4>
                    <p className="text-[10px] font-mono text-slate-400">{node.id}</p>
                  </div>
                </div>
                <div className="flex gap-10 items-center">
                  <div className="text-center">
                    <p className="text-[9px] font-bold text-slate-400 uppercase">Latencia</p>
                    <p className="font-bold text-slate-700">{node.latency}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[9px] font-bold text-slate-400 uppercase">Carga CPU</p>
                    <p className="font-bold text-slate-700">{node.load}</p>
                  </div>
                  <div className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter ${
                    node.status === 'online' ? 'bg-emerald-100 text-emerald-700' : 
                    node.status === 'warning' ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'
                  }`}>
                    {node.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'search' && (
          <div className="max-w-2xl mx-auto text-center mt-20">
            <div className="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center text-white mx-auto mb-6 shadow-xl shadow-blue-100">
              <BrainCircuit size={32} />
            </div>
            <h2 className="text-3xl font-black text-slate-800 mb-4">IA Consultor Técnico</h2>
            <p className="text-slate-500 mb-8">Pregunta sobre protocolos, estados de nodos o solicita un diagnóstico preventivo.</p>
            <div className="relative">
              <input 
                type="text" 
                placeholder="Ej: ¿Cuál es el impacto de latencia en el Nodo Sur?" 
                className="w-full p-5 pl-8 pr-32 rounded-2xl border border-slate-200 shadow-sm focus:ring-4 focus:ring-blue-100 focus:outline-none transition-all"
              />
              <button className="absolute right-2 top-2 bottom-2 bg-slate-900 text-white px-6 rounded-xl font-bold text-sm">Consultar</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
