import React, { useState, useEffect, useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell 
} from 'recharts';
import { 
  Activity, 
  ShieldCheck, 
  AlertTriangle, 
  Server, 
  Search, 
  RefreshCw, 
  Download, 
  Menu,
  Clock,
  Wifi,
  Globe
} from 'lucide-react';

const apiKey = "";

const App = () => {
  // --- State Management ---
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [lastUpdate, setLastUpdate] = useState(new Date().toLocaleTimeString());

  // --- Mock Data ---
  const metricsData = [
    { name: '00:00', latency: 45, bandwidth: 65, status: 'Normal' },
    { name: '04:00', latency: 42, bandwidth: 40, status: 'Normal' },
    { name: '08:00', latency: 85, bandwidth: 92, status: 'High' },
    { name: '12:00', latency: 60, bandwidth: 88, status: 'Normal' },
    { name: '16:00', latency: 55, bandwidth: 75, status: 'Normal' },
    { name: '20:00', latency: 48, bandwidth: 60, status: 'Normal' },
  ];

  const distributionData = [
    { name: 'Activo', value: 85, color: '#10b981' },
    { name: 'Mantenimiento', value: 10, color: '#f59e0b' },
    { name: 'Crítico', value: 5, color: '#ef4444' },
  ];

  const incidents = [
    { id: 'INC-001', service: 'Core Router AR-01', impact: 'Crítico', status: 'En Progreso', time: '10:45 AM' },
    { id: 'INC-002', service: 'Cloud Gateway West', impact: 'Bajo', status: 'Resuelto', time: '09:20 AM' },
    { id: 'INC-003', service: 'VPN Auth Service', impact: 'Medio', status: 'Abierto', time: '11:15 AM' },
    { id: 'INC-004', service: 'Database Cluster B', impact: 'Alto', status: 'Monitoreando', time: '10:05 AM' },
  ];

  // --- Gemini Search API Integration ---
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    let retries = 0;
    const maxRetries = 5;

    const performSearch = async () => {
      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: searchQuery }] }],
            tools: [{ "google_search": {} }]
          })
        });

        if (!response.ok) throw new Error('API Error');
        
        const result = await response.json();
        const sources = result.candidates?.[0]?.groundingMetadata?.groundingAttributions?.map(a => ({
          uri: a.web?.uri,
          title: a.web?.title
        })) || [];
        
        setSearchResults(sources);
      } catch (error) {
        if (retries < maxRetries) {
          const delay = Math.pow(2, retries) * 1000;
          retries++;
          setTimeout(performSearch, delay);
        } else {
          setSearchResults([{ title: "Error en la búsqueda", uri: "#" }]);
        }
      } finally {
        setLoading(false);
      }
    };

    performSearch();
  };

  const refreshDashboard = () => {
    setLoading(true);
    setTimeout(() => {
      setLastUpdate(new Date().toLocaleTimeString());
      setLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar / Navigation */}
      <nav className="fixed top-0 left-0 h-full w-20 md:w-64 bg-slate-900 text-white z-50 flex flex-col items-center py-6 shadow-2xl">
        <div className="mb-10 flex items-center gap-2 px-4">
          <Activity className="text-blue-400 w-8 h-8" />
          <span className="hidden md:block font-bold text-xl tracking-tight uppercase">Meru NOC</span>
        </div>
        
        <div className="flex flex-col w-full gap-2 px-2">
          {[
            { id: 'dashboard', icon: Server, label: 'Dashboard' },
            { id: 'network', icon: Globe, label: 'Red Global' },
            { id: 'alerts', icon: AlertTriangle, label: 'Alertas' },
            { id: 'search', icon: Search, label: 'IA Consultor' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center gap-4 p-3 rounded-lg transition-all ${
                activeTab === item.id ? 'bg-blue-600 text-white' : 'hover:bg-slate-800 text-slate-400'
              }`}
            >
              <item.icon size={24} />
              <span className="hidden md:block font-medium">{item.label}</span>
            </button>
          ))}
        </div>

        <div className="mt-auto w-full px-4 text-xs text-slate-500 hidden md:block">
          <p>© 2024 Meru NOC v2.0</p>
        </div>
      </nav>

      {/* Main Content */}
      <main className="ml-20 md:ml-64 p-4 md:p-8 pt-6">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-800">Panel de Control Operativo</h1>
            <p className="text-slate-500 flex items-center gap-2 mt-1">
              <Clock size={14} /> Última actualización: {lastUpdate}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={refreshDashboard}
              className="flex items-center gap-2 bg-white border border-slate-200 px-4 py-2 rounded-lg shadow-sm hover:bg-slate-50 active:scale-95 transition-all text-sm font-medium"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Sincronizar
            </button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg shadow-blue-200 hover:bg-blue-700 active:scale-95 transition-all text-sm font-medium flex items-center gap-2">
              <Download size={16} /> Exportar Reporte
            </button>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Quick Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
              {[
                { label: 'Uptime Global', value: '99.98%', sub: '+0.02%', color: 'text-emerald-600', bg: 'bg-emerald-50', icon: ShieldCheck },
                { label: 'Latencia Media', value: '52ms', sub: '-5ms', color: 'text-blue-600', bg: 'bg-blue-50', icon: Activity },
                { label: 'Alertas Activas', value: '12', sub: '3 Críticas', color: 'text-amber-600', bg: 'bg-amber-50', icon: AlertTriangle },
                { label: 'Uso de Tráfico', value: '1.2 TB', sub: 'Pico: 1.8 TB', color: 'text-indigo-600', bg: 'bg-indigo-50', icon: Wifi }
              ].map((m, i) => (
                <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center justify-between">
                  <div>
                    <p className="text-slate-500 text-sm font-medium mb-1">{m.label}</p>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold text-slate-800">{m.value}</span>
                      <span className={`text-xs font-semibold ${m.color}`}>{m.sub}</span>
                    </div>
                  </div>
                  <div className={`${m.bg} p-3 rounded-xl`}>
                    <m.icon className={m.color} size={24} />
                  </div>
                </div>
              ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Bandwidth vs Latency */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                  <Activity size={18} className="text-blue-500" /> Rendimiento en Tiempo Real
                </h3>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={metricsData}>
                      <defs>
                        <linearGradient id="colorBand" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                      <Tooltip 
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                      />
                      <Area type="monotone" dataKey="bandwidth" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorBand)" />
                      <Line type="monotone" dataKey="latency" stroke="#f43f5e" strokeWidth={2} dot={{ r: 4 }} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Status Distribution */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                  <ShieldCheck size={18} className="text-emerald-500" /> Estado de Dispositivos
                </h3>
                <div className="h-[300px] w-full flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={distributionData}
                        innerRadius={80}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {distributionData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-bold text-slate-800">142</span>
                    <span className="text-xs text-slate-400 font-medium">TOTAL NODOS</span>
                  </div>
                </div>
                <div className="flex justify-center gap-6 mt-4">
                  {distributionData.map((d, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: d.color}}></div>
                      <span className="text-xs font-medium text-slate-600">{d.name} ({d.value}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Incidents Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-800">Incidentes Recientes</h3>
                <span className="text-xs font-bold px-3 py-1 bg-slate-100 text-slate-600 rounded-full">Ver todos</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="bg-slate-50/50">
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">ID / Servicio</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Prioridad</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</th>
                      <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Hora Reporte</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {incidents.map((incident) => (
                      <tr key={incident.id} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex flex-col">
                            <span className="text-sm font-bold text-slate-700">{incident.service}</span>
                            <span className="text-xs text-slate-400 font-mono">{incident.id}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                            incident.impact === 'Crítico' ? 'bg-rose-100 text-rose-600' :
                            incident.impact === 'Alto' ? 'bg-orange-100 text-orange-600' :
                            'bg-blue-100 text-blue-600'
                          }`}>
                            {incident.impact}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm font-medium text-slate-600">{incident.status}</span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500 italic">
                          {incident.time}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'search' && (
          <div className="max-w-4xl mx-auto py-8">
            <div className="text-center mb-10">
              <div className="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-xl shadow-blue-100">
                <Search className="text-white" size={32} />
              </div>
              <h2 className="text-3xl font-bold text-slate-800 mb-2">Asistente Inteligente Meru</h2>
              <p className="text-slate-500 text-lg">Consulta estados, averías históricas o mejores prácticas de red.</p>
            </div>

            <form onSubmit={handleSearch} className="relative mb-12">
              <input 
                type="text" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Escribe tu consulta... (ej: ¿Cómo mejorar latencia en saltos de red?)"
                className="w-full bg-white border-2 border-slate-100 rounded-2xl px-6 py-5 pr-16 shadow-lg text-lg focus:border-blue-500 focus:outline-none transition-all placeholder:text-slate-400"
              />
              <button 
                type="submit"
                disabled={loading}
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {loading ? <RefreshCw className="animate-spin" size={24} /> : <Search size={24} />}
              </button>
            </form>

            <div className="grid gap-6">
              {searchResults.length > 0 ? (
                searchResults.map((result, idx) => (
                  <a 
                    key={idx} 
                    href={result.uri} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex gap-4">
                        <div className="bg-slate-100 p-3 rounded-lg group-hover:bg-blue-50 transition-colors">
                          <Globe size={24} className="text-slate-400 group-hover:text-blue-500" />
                        </div>
                        <div>
                          <h4 className="text-lg font-bold text-slate-800 group-hover:text-blue-600 transition-colors">{result.title}</h4>
                          <p className="text-sm text-slate-500 mt-1 line-clamp-1">{result.uri}</p>
                        </div>
                      </div>
                      <span className="text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">Ir al sitio &rarr;</span>
                    </div>
                  </a>
                ))
              ) : (
                !loading && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      "Análisis de tráfico semanal",
                      "Estado de repetidores Mérida",
                      "Optimización de BGP",
                      "Manual de contingencia"
                    ].map((suggestion, i) => (
                      <button 
                        key={i} 
                        onClick={() => setSearchQuery(suggestion)}
                        className="p-4 bg-white border border-slate-100 rounded-xl text-left text-slate-600 hover:border-blue-200 hover:bg-blue-50/50 transition-all text-sm font-medium"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )
              )}
            </div>
          </div>
        )}

      </main>
    </div>
  );
};

export default App;
