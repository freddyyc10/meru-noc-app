import React, { useState, useEffect, useRef } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, PieChart, Pie, Cell 
} from 'recharts';
import { 
  LayoutDashboard, 
  Search, 
  Server, 
  Activity, 
  ShieldCheck, 
  AlertTriangle, 
  RefreshCw, 
  Wifi, 
  ChevronRight,
  Settings,
  Bell,
  Download,
  FileUp,
  FileText,
  CheckCircle2,
  XCircle,
  BrainCircuit
} from 'lucide-react';

const apiKey = "";

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isExporting, setIsExporting] = useState(false);
  const [aiReport, setAiReport] = useState(null);
  const [nodes, setNodes] = useState([
    { id: 'ND-001', name: 'Nodo Norte - Caracas', status: 'online', latency: '12ms', load: '45%' },
    { id: 'ND-002', name: 'Nodo Centro - Maracay', status: 'online', latency: '18ms', load: '62%' },
    { id: 'ND-003', name: 'Nodo Sur - Bolívar', status: 'warning', latency: '85ms', load: '88%' },
    { id: 'ND-004', name: 'Nodo Occidente - Zulia', status: 'offline', latency: '0ms', load: '0%' },
  ]);

  // Datos para gráficos
  const chartData = [
    { name: '00:00', latency: 45, traffic: 400 },
    { name: '04:00', latency: 42, traffic: 300 },
    { name: '08:00', latency: 85, traffic: 800 },
    { name: '12:00', latency: 60, traffic: 750 },
    { name: '16:00', latency: 55, traffic: 600 },
    { name: '20:00', latency: 48, traffic: 450 },
  ];

  const generateAIReport = async (csvData) => {
    setLoading(true);
    setAiReport(null);
    
    const prompt = `Analiza los siguientes datos de red extraídos de un CSV y genera un informe ejecutivo breve (máximo 4 puntos clave) con recomendaciones: ${csvData}`;

    let attempts = 0;
    const maxAttempts = 5;

    const fetchReport = async () => {
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

        if (!response.ok) throw new Error('Error en IA');
        
        const data = await response.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
        setAiReport(text);
      } catch (err) {
        if (attempts < maxAttempts) {
          const delay = Math.pow(2, attempts) * 1000;
          attempts++;
          setTimeout(fetchReport, delay);
        } else {
          setAiReport("No se pudo generar el informe automático. Por favor, intente de nuevo.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
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
          // Simulamos que el contenido del CSV se envía a la IA
          const content = event.target.result.substring(0, 1000); // Primeros 1000 caracteres
          generateAIReport(content);
          setActiveTab('dashboard'); // Volver al dashboard para ver el informe
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;
    setLoading(true);
    // ... lógica de búsqueda ya existente ...
    setLoading(false);
  };

  const handleExport = () => {
    setIsExporting(true);
    setTimeout(() => {
      setIsExporting(false);
      // Simulación de descarga
      const blob = new Blob([aiReport || "Informe de Red Meru"], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'informe-noc-meru.txt';
      a.click();
    }, 1500);
  };

  return (
    <div className="flex min-h-screen bg-[#f8fafc]">
      {/* Sidebar - NO MODIFICAR */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed">
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Server className="text-white" size={20} />
            </div>
            <span className="font-bold text-xl text-slate-800 tracking-tight">Meru NOC</span>
          </div>
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
            <span className="font-semibold text-sm">Configuración</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64">
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 h-16 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">NOC</span>
            <ChevronRight size={14} className="text-slate-400" />
            <span className="text-slate-800 font-bold capitalize">{activeTab}</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button 
                onClick={handleImportCSV}
                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-white rounded-lg transition-all shadow-none hover:shadow-sm"
              >
                <FileUp size={14} className="text-blue-600" /> Importar CSV
              </button>
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-slate-700 hover:bg-white rounded-lg transition-all shadow-none hover:shadow-sm"
              >
                {isExporting ? <RefreshCw size={14} className="animate-spin text-blue-600" /> : <Download size={14} className="text-blue-600" />}
                Exportar Informe
              </button>
            </div>
          </div>
        </header>

        <div className="p-8">
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              {/* Alerta de Informe IA si existe */}
              {loading && (
                <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg flex items-center gap-4 animate-pulse">
                  <BrainCircuit size={32} className="animate-bounce" />
                  <div>
                    <h3 className="font-bold text-lg">Analizando datos con IA...</h3>
                    <p className="text-blue-100 text-sm">Procesando el archivo CSV para generar el informe ejecutivo.</p>
                  </div>
                </div>
              )}

              {aiReport && !loading && (
                <div className="bg-white border-2 border-blue-100 p-6 rounded-2xl shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-10">
                    <BrainCircuit size={80} className="text-blue-600" />
                  </div>
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-blue-600 p-2 rounded-lg text-white">
                      <FileText size={18} />
                    </div>
                    <h3 className="font-bold text-slate-800">Informe Ejecutivo Generado por IA</h3>
                  </div>
                  <div className="prose prose-slate max-w-none">
                    <p className="text-slate-600 leading-relaxed whitespace-pre-line font-medium">
                      {aiReport}
                    </p>
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-100 flex justify-end">
                    <button onClick={handleExport} className="text-xs font-bold text-blue-600 hover:underline">Descargar este informe como PDF</button>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-200">
                  <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">Tráfico Global</h3>
                  <p className="text-2xl font-black text-slate-800">1.84 Tbps</p>
                  <div className="mt-2 text-[10px] font-bold text-emerald-500 flex items-center gap-1">
                    <Activity size={10} /> +12.4% vs ayer
                  </div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200">
                  <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">Latencia Avg</h3>
                  <p className="text-2xl font-black text-slate-800">24.2 ms</p>
                  <div className="mt-2 text-[10px] font-bold text-blue-500">Estable</div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200">
                  <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">Seguridad</h3>
                  <p className="text-2xl font-black text-slate-800">Protegido</p>
                  <div className="mt-2 text-[10px] font-bold text-emerald-500">Sin brechas detectadas</div>
                </div>
                <div className="bg-white p-6 rounded-2xl border border-slate-200">
                  <h3 className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-2">Uptime</h3>
                  <p className="text-2xl font-black text-slate-800">99.98%</p>
                  <div className="mt-2 text-[10px] font-bold text-slate-400">Últimos 30 días</div>
                </div>
              </div>

              <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 mb-6">Actividad de Red en Tiempo Real</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Area type="monotone" dataKey="traffic" stroke="#3b82f6" fill="#eff6ff" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'nodos' && (
            <div className="space-y-6">
              <div className="flex justify-between items-end mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800">Gestión de Nodos</h2>
                  <p className="text-slate-500">Monitorización de puntos críticos de la red.</p>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2">
                  <RefreshCw size={16} /> Refrescar Estados
                </button>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {nodes.map(node => (
                  <div key={node.id} className="bg-white p-6 rounded-2xl border border-slate-200 flex items-center justify-between hover:border-blue-200 transition-colors">
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
                        <span className="block text-[10px] font-bold text-slate-400 uppercase">Carga CPU</span>
                        <div className="w-24 bg-slate-100 h-2 rounded-full mt-1">
                          <div 
                            className={`h-full rounded-full ${node.status === 'online' ? 'bg-blue-500' : 'bg-amber-500'}`} 
                            style={{ width: node.load }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-32 flex flex-col items-end">
                        <span className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase ${
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
            <div className="max-w-4xl mx-auto py-10">
              <div className="text-center mb-10">
                <div className="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                  <Search className="text-white" size={32} />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-2">Meru IA Consultor</h2>
                <p className="text-slate-500">¿En qué puedo ayudarte con la infraestructura hoy?</p>
              </div>
              
              <form onSubmit={handleSearch} className="relative mb-12">
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Escribe tu consulta técnica aquí..."
                  className="w-full bg-white border border-slate-200 rounded-3xl px-8 py-6 text-lg shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 transition-all pr-40"
                />
                <button 
                  type="submit"
                  disabled={loading}
                  className="absolute right-4 top-4 bottom-4 bg-slate-900 text-white px-10 rounded-2xl font-bold hover:bg-blue-600 transition-all disabled:bg-slate-300"
                >
                  {loading ? 'Consultando...' : 'Consultar'}
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
