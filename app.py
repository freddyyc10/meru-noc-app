import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area 
} from 'recharts';
import { 
  LayoutDashboard, 
  Database, 
  Activity, 
  AlertTriangle, 
  Upload, 
  Cpu, 
  ChevronRight,
  Search,
  Zap
} from 'lucide-react';

// --- Componentes Atómicos (Simulando la carpeta /components) ---

const Card = ({ title, value, icon: Icon, trend, color }) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-slate-400 text-sm font-medium">{title}</p>
        <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
        {trend && (
          <span className={`text-xs font-semibold mt-2 inline-block ${trend.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
            {trend} vs ayer
          </span>
        )}
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
    </div>
  </div>
);

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
      active ? 'bg-blue-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </button>
);

// --- Aplicación Principal ---

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Datos Mock de Telemetría (Simulando carga de CSV iDirect)
  const [data, setData] = useState([
    { time: '08:00', site1_ebno: 8.2, site1_traffic: 450, site2_ebno: 7.1 },
    { time: '09:00', site1_ebno: 7.9, site1_traffic: 520, site2_ebno: 6.8 },
    { time: '10:00', site1_ebno: 5.4, site1_traffic: 310, site2_ebno: 4.2 }, // Caída
    { time: '11:00', site1_ebno: 8.1, site1_traffic: 480, site2_ebno: 7.0 },
    { time: '12:00', site1_ebno: 8.5, site1_traffic: 600, site2_ebno: 7.5 },
  ]);

  const runAIAnalysis = async () => {
    setIsAnalyzing(true);
    const apiKey = ""; // Se inyecta automáticamente
    const model = "gemini-2.5-flash-preview-09-2025";
    
    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{ text: "Analiza esta telemetría satelital: Site 1 Eb/No bajó a 5.4 a las 10:00. Site 2 bajó a 4.2. ¿Es interferencia o lluvia? Responde en español de forma ejecutiva." }]
          }]
        })
      });
      const result = await response.json();
      setAiAnalysis(result.candidates[0].content.parts[0].text);
    } catch (error) {
      setAiAnalysis("Error conectando con Gemini. Revisa la consola.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col">
        <div className="flex items-center space-x-3 mb-10 px-2">
          <div className="bg-blue-600 p-2 rounded-lg">
            <Activity className="text-white" size={24} />
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Meru NOC</h1>
        </div>

        <nav className="flex-1 space-y-2">
          <SidebarItem 
            icon={LayoutDashboard} 
            label="Dashboard" 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')} 
          />
          <SidebarItem 
            icon={Database} 
            label="Reportes CSV" 
            active={activeTab === 'reports'} 
            onClick={() => setActiveTab('reports')} 
          />
          <SidebarItem 
            icon={Zap} 
            label="IA Predictiva" 
            active={activeTab === 'ai'} 
            onClick={() => setActiveTab('ai')} 
          />
        </nav>

        <div className="mt-auto pt-6 border-t border-slate-800 text-xs text-slate-500">
          v2.5.0-Intelligent <br />
          Meru Networks © 2024
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-slate-950 p-8">
        {/* Top Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-white">Consola de Operaciones</h2>
            <p className="text-slate-400 mt-1">Monitoreo de red satelital en tiempo real</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <input 
                type="text" 
                placeholder="Buscar estación..." 
                className="bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center space-x-2">
              <Upload size={16} />
              <span>Subir iDirect</span>
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card title="Terminales Online" value="1,284" icon={Cpu} trend="+12" color="bg-emerald-600" />
          <Card title="Eb/No Promedio" value="7.8 dB" icon={Activity} trend="-0.4" color="bg-blue-600" />
          <Card title="Tráfico Total" value="4.2 Gbps" icon={Zap} trend="+8%" color="bg-amber-600" />
          <Card title="Alertas Activas" value="3" icon={AlertTriangle} trend="-2" color="bg-rose-600" />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 p-6 rounded-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-bold text-white">Desempeño de Señal (Eb/No)</h3>
              <select className="bg-slate-800 border-none text-xs rounded px-2 py-1">
                <option>Últimas 24 horas</option>
                <option>Última semana</option>
              </select>
            </div>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorEbno" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="site1_ebno" stroke="#3b82f6" fillOpacity={1} fill="url(#colorEbno)" strokeWidth={3} />
                  <Area type="monotone" dataKey="site2_ebno" stroke="#f59e0b" fillOpacity={0} strokeWidth={2} strokeDasharray="5 5" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* AI Analysis Sidebar in UI */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex flex-col">
            <div className="flex items-center space-x-2 mb-4">
              <Cpu className="text-purple-400" size={20} />
              <h3 className="text-lg font-bold text-white">Diagnóstico IA</h3>
            </div>
            
            <div className="flex-1 bg-slate-950/50 rounded-lg p-4 border border-slate-800/50 text-sm overflow-y-auto">
              {aiAnalysis ? (
                <div className="animate-in fade-in duration-500">
                  <p className="text-slate-300 leading-relaxed italic">
                    "{aiAnalysis}"
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center text-slate-500">
                  <Activity size={40} className="mb-4 opacity-20" />
                  <p>Inicia el análisis para detectar anomalías en la telemetría.</p>
                </div>
              )}
            </div>

            <button 
              onClick={runAIAnalysis}
              disabled={isAnalyzing}
              className={`mt-4 w-full py-3 rounded-lg font-bold flex items-center justify-center space-x-2 transition-all ${
                isAnalyzing ? 'bg-slate-800 text-slate-500' : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg shadow-blue-900/20'
              }`}
            >
              {isAnalyzing ? (
                <div className="animate-spin h-5 w-5 border-2 border-slate-400 border-t-transparent rounded-full" />
              ) : (
                <>
                  <Zap size={18} />
                  <span>Analizar Anomalías</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Recent Events / Table */}
        <div className="mt-8 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-800">
            <h3 className="text-lg font-bold text-white">Alertas Recientes del HUB</h3>
          </div>
          <table className="w-full text-left">
            <thead className="bg-slate-800/50 text-slate-400 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4 font-medium">Estación / Remote</th>
                <th className="px-6 py-4 font-medium">Evento</th>
                <th className="px-6 py-4 font-medium">Estado</th>
                <th className="px-6 py-4 font-medium">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {[
                { name: 'Site_Antarctica_01', event: 'Low Eb/No Threshold', status: 'Crítico', color: 'text-rose-500' },
                { name: 'Site_Bogota_HUB', event: 'Peak Traffic Reached', status: 'Advertencia', color: 'text-amber-500' },
                { name: 'Remote_Quito_22', event: 'Re-acquisition Success', status: 'Normal', color: 'text-emerald-500' },
              ].map((row, i) => (
                <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4 font-semibold text-slate-200">{row.name}</td>
                  <td className="px-6 py-4 text-sm text-slate-400">{row.event}</td>
                  <td className={`px-6 py-4 text-sm font-bold ${row.color}`}>{row.status}</td>
                  <td className="px-6 py-4">
                    <button className="text-blue-400 hover:text-blue-300 flex items-center text-xs font-bold">
                      DETALLES <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
