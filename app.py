import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell
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
  Zap
} from 'lucide-react';

const App = () => {
  const [dataEbNo, setDataEbNo] = useState([]);
  const [dataUsage, setDataUsage] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');

  // Simulación de procesamiento de los archivos subidos (Statistics 44 y Usage 20)
  useEffect(() => {
    // Datos de ejemplo basados en los archivos del usuario
    const mockEbNo = [
      { time: '10:00', station: 'AMA05_CAICET', fl: 14.6, rl: 9.2 },
      { time: '10:10', station: 'AMA05_CAICET', fl: 14.7, rl: 9.0 },
      { time: '10:20', station: 'AMA05_CAICET', fl: 14.5, rl: 8.8 },
      { time: '10:00', station: 'DC72_WARAIRAREPANO', fl: 15.6, rl: 10.2 },
      { time: '10:10', station: 'DC72_WARAIRAREPANO', fl: 15.5, rl: 10.4 },
      { time: '10:00', station: 'ARA16_VALLE_MORIN', fl: 13.8, rl: 9.5 },
      { time: '10:10', station: 'ARA16_VALLE_MORIN', fl: 12.9, rl: 9.2 },
    ];

    const mockUsage = [
      { station: 'ARA16_VALLE_MORIN', in: 450, out: 120 },
      { station: 'DC72_WARAIRAREPANO', in: 380, out: 85 },
      { station: 'AMA05_CAICET', in: 110, out: 15 },
      { station: 'AMA13_RUHUODE', in: 95, out: 12 },
    ];

    setDataEbNo(mockEbNo);
    setDataUsage(mockUsage);
  }, []);

  // Lógica de Análisis de Ingeniería
  const engineeringAnalysis = useMemo(() => {
    const critical = [];
    const stable = [];
    
    // Agrupar por estación para promediar
    const stations = [...new Set(dataEbNo.map(d => d.station))];
    
    stations.forEach(name => {
      const readings = dataEbNo.filter(d => d.station === name);
      const avgRL = readings.reduce((acc, curr) => acc + curr.rl, 0) / readings.length;
      const avgFL = readings.reduce((acc, curr) => acc + curr.fl, 0) / readings.length;
      const usage = dataUsage.find(u => u.station === name) || { in: 0, out: 0 };

      const status = {
        name,
        avgRL,
        avgFL,
        totalTraffic: usage.in + usage.out,
        health: avgRL < 9.5 ? 'critical' : (avgRL < 10.5 ? 'warning' : 'good'),
        recommendation: ''
      };

      if (status.health === 'critical') {
        status.recommendation = "Realizar Peaking de antena (RL bajo el umbral).";
        critical.push(status);
      } else {
        stable.push(status);
      }
    });

    return { critical, stable };
  }, [dataEbNo, dataUsage]);

  const SummaryCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold mt-1 text-slate-800">{value}</h3>
        </div>
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans p-4 md:p-8">
      {/* Header */}
      <header className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 flex items-center gap-2">
            <Zap className="text-blue-600" fill="currentColor" /> VNO Meru <span className="text-slate-400 font-light">|</span> Analyzer
          </h1>
          <p className="text-slate-500">Sistema Integrado de Diagnóstico de Ingeniería Satelital</p>
        </div>
        <div className="flex items-center gap-2 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'dashboard' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            Dashboard
          </button>
          <button 
            onClick={() => setActiveTab('analysis')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'analysis' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-600 hover:bg-slate-50'}`}
          >
            Análisis Técnico
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto">
        {activeTab === 'dashboard' ? (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <SummaryCard title="Estaciones Activas" value="54" icon={Activity} color="bg-blue-500" />
              <SummaryCard title="Eb/No Promedio (FL)" value="14.8 dB" icon={CheckCircle} color="bg-emerald-500" />
              <SummaryCard title="Alertas Críticas" value={engineeringAnalysis.critical.length} icon={AlertTriangle} color="bg-red-500" />
              <SummaryCard title="Tráfico Total (24h)" value="1.2 TB" icon={Database} color="bg-indigo-500" />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <BarChart3 size={18} className="text-blue-600" /> Consumo por Estación (Top 5)
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dataUsage.slice(0, 5)}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="station" fontSize={10} tick={{fill: '#64748b'}} />
                      <YAxis fontSize={10} tick={{fill: '#64748b'}} />
                      <Tooltip 
                        contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}}
                      />
                      <Bar dataKey="in" name="Inbound (MB)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="out" name="Outbound (MB)" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Activity size={18} className="text-blue-600" /> Comportamiento Eb/No (Return Link)
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dataEbNo.filter(d => d.station === 'AMA05_CAICET')}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="time" fontSize={10} tick={{fill: '#64748b'}} />
                      <YAxis domain={[7, 12]} fontSize={10} tick={{fill: '#64748b'}} />
                      <Tooltip />
                      <Legend verticalAlign="top" height={36} iconType="circle" />
                      <Line type="monotone" dataKey="rl" stroke="#ef4444" strokeWidth={3} dot={{r: 4}} name="RL AMA05" />
                      <Line type="monotone" dataKey="fl" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" name="FL AMA05" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in duration-500">
            {/* Engineering Analysis View */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div>
                    <h2 className="text-xl font-bold flex items-center gap-2">
                      <FileText className="text-blue-600" /> Diagnóstico Automático de Red
                    </h2>
                    <p className="text-sm text-slate-500">Cruce de parámetros físicos y lógicos (Eb/No vs Tráfico)</p>
                  </div>
                  <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                    <input 
                      type="text" 
                      placeholder="Buscar estación..." 
                      className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="p-0 overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 text-slate-500 text-xs uppercase tracking-wider font-semibold">
                      <th className="px-6 py-4">Estación</th>
                      <th className="px-6 py-4 text-center">RL Avg (dB)</th>
                      <th className="px-6 py-4 text-center">FL Avg (dB)</th>
                      <th className="px-6 py-4">Estado</th>
                      <th className="px-6 py-4">Recomendación Técnica</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {[...engineeringAnalysis.critical, ...engineeringAnalysis.stable]
                      .filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()))
                      .map((site, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 font-bold text-slate-700">{site.name}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`font-mono font-bold ${site.avgRL < 9.5 ? 'text-red-600' : 'text-slate-600'}`}>
                            {site.avgRL.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center font-mono text-slate-600">{site.avgFL.toFixed(2)}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                            site.health === 'critical' ? 'bg-red-100 text-red-700' : 
                            site.health === 'warning' ? 'bg-amber-100 text-amber-700' : 
                            'bg-emerald-100 text-emerald-700'
                          }`}>
                            {site.health === 'critical' ? <AlertTriangle size={12}/> : <CheckCircle size={12}/>}
                            {site.health.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {site.health === 'critical' ? (
                            <span className="flex items-start gap-2 text-red-600 font-medium italic">
                              <ArrowDownRight size={16} className="mt-0.5 shrink-0" />
                              {site.recommendation}
                            </span>
                          ) : (
                            <span className="flex items-center gap-2 text-slate-400">
                              <CheckCircle size={16} /> Parámetros en rango operativo.
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Insight Box */}
            <div className="bg-blue-600 rounded-xl p-6 text-white shadow-lg shadow-blue-200">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                <Zap size={20} /> Conclusión del Análisis
              </h3>
              <p className="text-blue-100 leading-relaxed">
                Se detectó una degradación significativa en el estado **Amazonas**. Las estaciones <code className="bg-blue-700 px-1 rounded text-white">AMA05_CAICET</code> presentan un Margen de Desvanecimiento crítico. Se recomienda ajustar el umbral de MODCOD para evitar la pérdida de sincronismo durante eventos climáticos menores.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
