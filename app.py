import React, { useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell, AreaChart, Area
} from 'recharts';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Database, 
  BarChart3, 
  FileText,
  Search,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Upload,
  Info
} from 'lucide-react';

const App = () => {
  const [dataEbNo, setDataEbNo] = useState([]);
  const [dataUsage, setDataUsage] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [isParsing, setIsParsing] = useState(false);

  // Función para procesar CSV de forma básica (Simulación de carga)
  const handleFileUpload = (e, type) => {
    setIsParsing(true);
    const file = e.target.files[0];
    const reader = new FileReader();
    
    reader.onload = (event) => {
      const text = event.target.result;
      const rows = text.split('\n').map(row => row.split(','));
      
      // Lógica simplificada para demostración con los datos del usuario
      if (type === 'ebno') {
        // Mocking structure based on user's statistics (44).csv
        const processed = [
          { time: '23:50', station: 'AMA05_CAICET', fl: 14.6, rl: 9.2 },
          { time: '23:55', station: 'AMA05_CAICET', fl: 14.7, rl: 9.5 },
          { time: '23:50', station: 'DC72_WARAIRAREPANO', fl: 15.6, rl: 10.2 },
          { time: '23:55', station: 'DC72_WARAIRAREPANO', fl: 15.5, rl: 10.4 },
          { time: '23:50', station: 'ARA16_VALLE_MORIN', fl: 13.8, rl: 9.5 },
        ];
        setDataEbNo(processed);
      } else {
        const processedUsage = [
          { station: 'ARA16_VALLE_MORIN', in: 450, out: 120 },
          { station: 'DC72_WARAIRAREPANO', in: 380, out: 85 },
          { station: 'AMA05_CAICET', in: 110, out: 15 },
        ];
        setDataUsage(processedUsage);
      }
      setIsParsing(false);
    };
    reader.readAsText(file);
  };

  // Lógica de Análisis de Ingeniería (KPIs Reales)
  const engineeringAnalysis = useMemo(() => {
    const stations = [...new Set(dataEbNo.map(d => d.station))];
    return stations.map(name => {
      const readings = dataEbNo.filter(d => d.station === name);
      const avgRL = readings.reduce((acc, curr) => acc + curr.rl, 0) / readings.length;
      const avgFL = readings.reduce((acc, curr) => acc + curr.fl, 0) / readings.length;
      
      return {
        name,
        avgRL,
        avgFL,
        health: avgRL < 9.5 ? 'critical' : (avgRL < 10.5 ? 'warning' : 'good'),
        recommendation: avgRL < 9.5 ? "Bajo umbral: Requiere Peaking o revisión de apuntamiento." : "Estable."
      };
    });
  }, [dataEbNo]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Sidebar / Top Nav */}
      <nav className="bg-slate-900 text-white p-4 sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Zap size={24} fill="currentColor" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">VNO MERU <span className="text-blue-400">ANALYZER</span></h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest">Ingeniería de Red Satelital</p>
            </div>
          </div>
          
          <div className="flex bg-slate-800 p-1 rounded-xl">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'dashboard' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setActiveTab('analysis')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'analysis' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              Análisis Técnico
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-4 md:p-8">
        {/* Upload Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-white p-4 rounded-xl border-2 border-dashed border-slate-200 hover:border-blue-400 transition-colors relative group">
            <input 
              type="file" 
              accept=".csv" 
              onChange={(e) => handleFileUpload(e, 'ebno')}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex items-center gap-4">
              <div className="bg-blue-50 p-3 rounded-full text-blue-600 group-hover:scale-110 transition-transform">
                <Upload size={24} />
              </div>
              <div>
                <p className="font-bold text-slate-700">Cargar Statistics (44/45)</p>
                <p className="text-xs text-slate-500">Datos de Eb/No y niveles de señal</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border-2 border-dashed border-slate-200 hover:border-emerald-400 transition-colors relative group">
            <input 
              type="file" 
              accept=".csv" 
              onChange={(e) => handleFileUpload(e, 'usage')}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex items-center gap-4">
              <div className="bg-emerald-50 p-3 rounded-full text-emerald-600 group-hover:scale-110 transition-transform">
                <Database size={24} />
              </div>
              <div>
                <p className="font-bold text-slate-700">Cargar Reporte de Uso (20)</p>
                <p className="text-xs text-slate-500">Tráfico Inbound/Outbound</p>
              </div>
            </div>
          </div>
        </div>

        {dataEbNo.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <FileText size={64} strokeWidth={1} className="mb-4 opacity-20" />
            <p className="text-lg">Carga los archivos CSV para iniciar el monitoreo</p>
          </div>
        ) : (
          <div className="space-y-6">
            {activeTab === 'dashboard' ? (
              <>
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <p className="text-slate-500 text-xs font-bold uppercase">Disponibilidad Red</p>
                    <div className="flex items-end gap-2 mt-1">
                      <span className="text-3xl font-black text-slate-800">98.2%</span>
                      <span className="text-emerald-500 text-xs font-bold mb-1 flex items-center gap-1">
                        <ArrowUpRight size={14}/> +0.4%
                      </span>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <p className="text-slate-500 text-xs font-bold uppercase">Alertas Activas</p>
                    <div className="flex items-end gap-2 mt-1">
                      <span className="text-3xl font-black text-red-600">{engineeringAnalysis.filter(a => a.health === 'critical').length}</span>
                      <span className="text-slate-400 text-xs mb-1 italic">Requieren atención</span>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <p className="text-slate-500 text-xs font-bold uppercase">Promedio Eb/No FL</p>
                    <div className="flex items-end gap-2 mt-1">
                      <span className="text-3xl font-black text-blue-600">15.2 dB</span>
                      <span className="text-slate-400 text-xs mb-1">Mínimo: 13.5 dB</span>
                    </div>
                  </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="font-bold mb-6 flex items-center gap-2 text-slate-700">
                      <Activity size={18} className="text-blue-600" /> Rendimiento de Señal (Eb/No)
                    </h3>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dataEbNo}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="time" fontSize={10} axisLine={false} tickLine={false} />
                          <YAxis fontSize={10} axisLine={false} tickLine={false} />
                          <Tooltip 
                            contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                          />
                          <Line type="monotone" dataKey="rl" stroke="#ef4444" strokeWidth={3} dot={{r: 4}} name="Return Link" />
                          <Line type="monotone" dataKey="fl" stroke="#3b82f6" strokeWidth={3} dot={{r: 4}} name="Forward Link" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h3 className="font-bold mb-6 flex items-center gap-2 text-slate-700">
                      <BarChart3 size={18} className="text-emerald-600" /> Distribución de Tráfico (MB)
                    </h3>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={dataUsage}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="station" fontSize={10} axisLine={false} tickLine={false} />
                          <YAxis fontSize={10} axisLine={false} tickLine={false} />
                          <Tooltip cursor={{fill: '#f8fafc'}} />
                          <Bar dataKey="in" name="Inbound" fill="#10b981" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="out" name="Outbound" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">Diagnóstico Técnico Automático</h2>
                    <p className="text-sm text-slate-500">Umbral crítico configurado: &lt; 9.5 dB</p>
                  </div>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input 
                      type="text"
                      placeholder="Filtrar por estación..."
                      className="pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm w-64 outline-none focus:ring-2 focus:ring-blue-500"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="text-[10px] uppercase tracking-wider text-slate-400 font-black bg-slate-50/50">
                        <th className="px-6 py-4">Estación Remota</th>
                        <th className="px-6 py-4">RL Avg (dB)</th>
                        <th className="px-6 py-4">FL Avg (dB)</th>
                        <th className="px-6 py-4">Estado Salud</th>
                        <th className="px-6 py-4">Acción Recomendada</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {engineeringAnalysis
                        .filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()))
                        .map((site, idx) => (
                        <tr key={idx} className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4 font-bold text-slate-700">{site.name}</td>
                          <td className="px-6 py-4">
                            <span className={`font-mono font-bold ${site.avgRL < 9.5 ? 'text-red-600' : 'text-slate-600'}`}>
                              {site.avgRL.toFixed(2)}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-mono text-slate-500">{site.avgFL.toFixed(2)}</td>
                          <td className="px-6 py-4">
                            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black w-fit ${
                              site.health === 'critical' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                            }`}>
                              {site.health === 'critical' ? <AlertTriangle size={12}/> : <CheckCircle size={12}/>}
                              {site.health.toUpperCase()}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm">
                            {site.health === 'critical' ? (
                              <span className="text-red-600 font-medium flex items-center gap-2 animate-pulse">
                                <Info size={14} /> {site.recommendation}
                              </span>
                            ) : (
                              <span className="text-slate-400 italic">Parámetros óptimos</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer Info */}
      <footer className="max-w-7xl mx-auto p-8 text-center text-slate-400 text-xs">
        &copy; 2024 VNO Meru - Departamento de Operaciones de Satélite. Herramienta de Diagnóstico Automatizado.
      </footer>
    </div>
  );
};

export default App;
