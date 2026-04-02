import React, { useState } from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import { 
  LayoutDashboard, 
  Search, 
  Server, 
  Activity, 
  ShieldCheck, 
  RefreshCw, 
  ChevronRight,
  Settings,
  Download,
  FileUp,
  FileText,
  CheckCircle2,
  XCircle,
  BrainCircuit,
  Bell
} from 'lucide-react';

const apiKey = "";

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [aiReport, setAiReport] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  // Datos simulados de Nodos
  const [nodes] = useState([
    { id: 'ND-001', name: 'Nodo Norte - Caracas', status: 'online', latency: '12ms', load: '45%' },
    { id: 'ND-002', name: 'Nodo Centro - Maracay', status: 'online', latency: '18ms', load: '62%' },
    { id: 'ND-003', name: 'Nodo Sur - Bolívar', status: 'warning', latency: '85ms', load: '88%' },
    { id: 'ND-004', name: 'Nodo Occidente - Zulia', status: 'offline', latency: '0ms', load: '0%' },
  ]);

  // Datos para gráficos de tráfico
  const chartData = [
    { name: '00:00', traffic: 400 },
    { name: '04:00', traffic: 300 },
    { name: '08:00', traffic: 800 },
    { name: '12:00', traffic: 750 },
    { name: '16:00', traffic: 600 },
    { name: '20:00', traffic: 450 },
  ];

  // Generar informe con IA a partir de datos CSV
  const generateAIReport = async (csvData) => {
    setLoading(true);
    setAiReport(null);
    
    const prompt = `Analiza estos datos de red extraídos de un archivo CSV y genera un informe ejecutivo breve para el NOC de Meru. Incluye: 1. Estado de salud general, 2. Puntos críticos detectados, 3. Recomendaciones técnicas inmediatas. Datos: ${csvData}`;

    try {
      const modelStr = "gemini-2.5-flash-preview-09-2025";
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${modelStr}:generateContent?key=${apiKey}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }]
        })
      });

      if (!response.ok) throw new Error('Error en la API');
      
      const data = await response.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
      setAiReport(text || "No se pudo generar el texto del informe.");
    } catch (err) {
      console.error(err);
      setAiReport("Error al conectar con la IA de Meru. Por favor, intente de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  // Manejar importación de CSV
  const handleImportCSV = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const content = event.target.result.substring(0, 2000);
          generateAIReport(content);
          setActiveTab('dashboard');
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      const text = aiReport || "Informe de Red Meru - Sin datos de IA procesados.";
      const blob = new Blob([text], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'informe-meru-noc.txt';
      a.click();
    }, 1000);
  };

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed">
        <div className="p-6 border-b border-slate-100 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg text-white">
            <Server size={20} />
          </div>
          <span className="font-bold text-xl text-slate-800 tracking-tight">Meru NOC</span>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activeTab === 'dashboard' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <LayoutDashboard size={20} />
            <span className="font-semibold text-sm">Dashboard</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('search')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activeTab === 'search' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Search size={20} />
            <span className="font-semibold text-sm">IA Consultor</span>
          </button>

          <div className="pt-6 pb-2 px-4">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Sistemas</span>
          </div>

          <button 
            onClick={() => setActiveTab('nodos')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activeTab === 'nodos' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <Activity size={20} />
            <span className="font-semibold text-sm">Nodos</span>
          </button>
          
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-50 transition-colors">
            <ShieldCheck size={20} />
            <span className="font-semibold text-sm">Seguridad</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-100">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-50 transition-colors">
            <Settings size={20} />
            <span className="font-semibold text-sm">Ajustes</span>
          </button>
        </div>
      </aside>

      {/* Área de Contenido Principal */}
      <main className="flex-1 ml-64 min-h-screen">
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium text-xs">NOC</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="text-slate-800 font-bold capitalize text-sm">
              {activeTab === 'search' ? 'IA Consultor' : activeTab}
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button 
                onClick={handleImportCSV}
                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-white rounded-lg transition-all"
              >
                <FileUp size={14} className="text-blue-600" /> Importar CSV
              </button>
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-white rounded-lg transition-all"
              >
                {isExporting ? <RefreshCw size={14} className="animate-spin text-blue-600" /> : <Download size={14} className="text-blue-600" />}
                Exportar Informe
              </button>
            </div>
            <button className="p-2 text-slate-400 hover:bg-slate-50 rounded-full relative transition-colors">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
          </div>
        </header>

        <div className="p-8">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {loading && (
                <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg flex items-center gap-4 animate-pulse">
                  <BrainCircuit size={32} className="animate-bounce" />
                  <div>
                    <h3 className="font-bold text-lg">Analizando datos con IA Meru...</h3>
                    <p className="text-blue-100 text-sm">Generando informe ejecutivo basado en el CSV importado.</p>
                  </div>
                </div>
              )}

              {aiReport && !loading && (
                <div className="bg-white border-2 border-blue-100 p-6 rounded-2xl shadow-sm relative overflow-hidden">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-blue-600 p-2 rounded-lg text-white">
                      <FileText size={18} />
                    </div>
                    <h3 className="font-bold text-slate-800">Informe Ejecutivo de IA</h3>
                  </div>
                  <div className="prose prose-slate max-w-none">
                    <p className="text-slate-600 whitespace-pre-line text-sm leading-relaxed font-medium">
                      {aiReport}
                    </p>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                  { label: 'Tráfico Global', val: '1.84 Tbps', change: '+12.4%' },
                  { label: 'Latencia Avg', val: '24.2 ms', change: 'Estable' },
                  { label: 'Seguridad', val: 'Protegido', change: 'Sin brechas' },
                  { label: 'Uptime', val: '99.98%', change: '30 días' }
                ].map((stat, i) => (
                  <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">{stat.label}</h3>
                    <p className="text-2xl font-black text-slate-800">{stat.val}</p>
                    <div className="mt-2 text-[10px] font-bold text-emerald-500">{stat.change}</div>
                  </div>
                ))}
              </div>

              <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 mb-6">Tráfico de Red en Tiempo Real</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                      <Tooltip />
                      <Area type="monotone" dataKey="traffic" stroke="#3b82f6" fill="#eff6ff" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'nodos' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-slate-800">Estado de Nodos</h2>
                <button className="bg-slate-100 text-slate-600 px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 hover:bg-slate-200 transition-all">
                  <RefreshCw size={16} /> Re-escaneo
                </button>
              </div>
              <div className="grid grid-cols-1 gap-4">
                {nodes.map(node => (
                  <div key={node.id} className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center justify-between hover:border-blue-300 transition-all shadow-sm">
                    <div className="flex items-center gap-6">
                      <div className={`p-4 rounded-2xl ${
                        node.status === 'online' ? 'bg-emerald-50 text-emerald-600' : 
                        node.status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600'
                      }`}>
                        <Server size={24} />
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-800">{node.name}</h4>
                        <p className="text-xs text-slate-400 font-mono">{node.id}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-12 text-center">
                      <div>
                        <span className="block text-[10px] font-bold text-slate-400 uppercase">Latencia</span>
                        <span className="font-bold text-slate-700">{node.latency}</span>
                      </div>
                      <div>
                        <span className="block text-[10px] font-bold text-slate-400 uppercase">Carga</span>
                        <span className="font-bold text-slate-700">{node.load}</span>
                      </div>
                      <div className="w-32">
                        <span className={`flex items-center justify-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase ${
                          node.status === 'online' ? 'bg-emerald-100 text-emerald-700' : 
                          node.status === 'warning' ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'
                        }`}>
                          {node.status === 'online' ? <CheckCircle2 size={12}/> : <XCircle size={12}/>}
                          {node.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'search' && (
            <div className="max-w-3xl mx-auto pt-16">
              <div className="text-center mb-10">
                <div className="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-200">
                  <BrainCircuit className="text-white" size={32} />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-2">IA Consultor Meru</h2>
                <p className="text-slate-500">Consulta estados críticos o solicita diagnósticos técnicos avanzados sobre la infraestructura.</p>
              </div>
              <form onSubmit={(e) => { e.preventDefault(); /* Lógica de búsqueda */ }} className="relative">
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Ej: ¿Por qué hay alta carga en el Nodo Sur?"
                  className="w-full bg-white border border-slate-200 rounded-3xl px-8 py-6 text-lg shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all"
                />
                <button className="absolute right-3 top-3 bottom-3 bg-slate-900 text-white px-8 rounded-2xl font-bold hover:bg-blue-600 transition-all">
                  Consultar
                </button>
              </form>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
