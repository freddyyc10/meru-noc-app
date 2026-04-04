import React, { useState, useMemo, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, AreaChart, Area
} from 'recharts';
import { 
  Activity, AlertTriangle, CheckCircle, Database, BarChart3, FileText, 
  Search, ArrowUpRight, Zap, Upload, Info, Network
} from 'lucide-react';

const App = () => {
  const [ebnoData, setEbnoData] = useState([]);
  const [usageData, setUsageData] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');

  // Procesador de CSV para Statistics (44) - Eb/No
  const processEbNoFile = (text) => {
    const lines = text.split('\n');
    if (lines.length < 2) return;
    
    const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));
    const results = [];

    // Tomamos las últimas 50 muestras para no saturar el gráfico
    const dataLines = lines.slice(1).filter(l => l.trim() !== '').slice(-50);

    dataLines.forEach(line => {
      const values = line.split(',');
      const timestamp = values[0].replace(/"/g, '').split(' ')[1] || '';
      
      // Buscamos columnas de AMA05_CAICET como ejemplo base
      const rlIdx = headers.findIndex(h => h.includes('AMA05_CAICET/RL'));
      const flIdx = headers.findIndex(h => h.includes('AMA05_CAICET/FL'));
      
      if (rlIdx !== -1 && flIdx !== -1) {
        results.push({
          time: timestamp,
          rl: parseFloat(values[rlIdx]) || null,
          fl: parseFloat(values[flIdx]) || null,
          station: 'AMA05_CAICET'
        });
      }
    });
    setEbnoData(results);
  };

  // Procesador de CSV para Data Usage (20)
  const processUsageFile = (text) => {
    const lines = text.split('\n');
    // El reporte 20 tiene encabezados en la línea 4 usualmente
    const dataLines = lines.slice(4).filter(l => l.trim() !== '');
    if (dataLines.length === 0) return;

    const headers = lines[3]?.split(',') || [];
    const lastRow = dataLines[dataLines.length - 1].split(',');
    
    const stations = [];
    headers.forEach((header, index) => {
      const cleanHeader = header.replace(/"/g, '');
      if (cleanHeader.includes(' In')) {
        const name = cleanHeader.replace(' In', '');
        stations.push({
          name: name,
          in: parseFloat(lastRow[index]) || 0,
          out: parseFloat(lastRow[index + 1]) || 0
        });
      }
    });
    setUsageData(stations.sort((a, b) => b.in - a.in).slice(0, 10));
  };

  const handleFile = (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      if (type === 'ebno') processEbNoFile(text);
      else processUsageFile(text);
    };
    reader.readAsText(file);
  };

  // Análisis de salud de estaciones
  const healthStats = useMemo(() => {
    if (ebnoData.length === 0) return [];
    // Agrupar por estación (en este ejemplo simplificado usamos una, pero se puede expandir)
    return [{
      name: 'AMA05_CAICET',
      avgRL: ebnoData.reduce((a, b) => a + (b.rl || 0), 0) / ebnoData.filter(d => d.rl).length,
      avgFL: ebnoData.reduce((a, b) => a + (b.fl || 0), 0) / ebnoData.filter(d => d.fl).length,
      status: ebnoData[ebnoData.length - 1]?.rl < 9.5 ? 'Crítico' : 'Estable'
    }];
  }, [ebnoData]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <header className="bg-slate-900 text-white p-4 shadow-xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Network size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">NOC MERU <span className="text-blue-400">ENGINEER</span></h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">VNO Monitoring System</p>
            </div>
          </div>
          
          <div className="flex bg-slate-800 p-1 rounded-xl">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'dashboard' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setActiveTab('inventory')}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'inventory' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400'}`}
            >
              Estado de Remotas
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {/* Panel de Carga */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-white p-5 rounded-2xl border-2 border-dashed border-gray-200 hover:border-blue-500 transition-all relative group shadow-sm">
            <input type="file" onChange={(e) => handleFile(e, 'ebno')} className="absolute inset-0 opacity-0 cursor-pointer" />
            <div className="flex items-center gap-4">
              <div className="bg-blue-50 p-3 rounded-xl text-blue-600 group-hover:scale-110 transition-transform">
                <Activity size={24} />
              </div>
              <div>
                <p className="font-bold text-gray-700">Cargar Statistics (44)</p>
                <p className="text-xs text-gray-500 font-medium">Niveles de Eb/No y RF</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-5 rounded-2xl border-2 border-dashed border-gray-200 hover:border-emerald-500 transition-all relative group shadow-sm">
            <input type="file" onChange={(e) => handleFile(e, 'usage')} className="absolute inset-0 opacity-0 cursor-pointer" />
            <div className="flex items-center gap-4">
              <div className="bg-emerald-50 p-3 rounded-xl text-emerald-600 group-hover:scale-110 transition-transform">
                <Database size={24} />
              </div>
              <div>
                <p className="font-bold text-gray-700">Cargar Usage Report (20)</p>
                <p className="text-xs text-gray-500 font-medium">Tráfico Inbound/Outbound</p>
              </div>
            </div>
          </div>
        </div>

        {ebnoData.length === 0 && usageData.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-gray-100 shadow-inner">
            <Zap size={48} className="text-gray-200 mb-4 animate-pulse" />
            <p className="text-gray-400 font-medium text-center">Esperando datos de entrada para generar el análisis...</p>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in duration-500">
            {activeTab === 'dashboard' ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-wider">Eb/No RL Promedio</p>
                    <p className="text-3xl font-black text-slate-800 mt-2">
                      {healthStats[0]?.avgRL?.toFixed(2) || '0.00'} <span className="text-sm font-normal text-gray-400">dB</span>
                    </p>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-wider">Tráfico Pico In</p>
                    <p className="text-3xl font-black text-emerald-600 mt-2">
                      {usageData[0]?.in?.toFixed(1) || '0.0'} <span className="text-sm font-normal text-gray-400">MB</span>
                    </p>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <p className="text-gray-400 text-xs font-bold uppercase tracking-wider">Alertas Activas</p>
                    <p className={`text-3xl font-black mt-2 ${healthStats.some(s => s.status === 'Crítico') ? 'text-red-600' : 'text-emerald-500'}`}>
                      {healthStats.filter(s => s.status === 'Crítico').length}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="font-bold mb-6 flex items-center gap-2 text-slate-700">
                      <Activity size={18} className="text-blue-600" /> Histórico de Eb/No (Real-Time)
                    </h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={ebnoData}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="time" fontSize={10} axisLine={false} />
                          <YAxis domain={[0, 20]} fontSize={10} axisLine={false} />
                          <Tooltip 
                            contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'}}
                          />
                          <Legend />
                          <Line type="monotone" dataKey="rl" name="Return Link" stroke="#ef4444" strokeWidth={3} dot={false} />
                          <Line type="monotone" dataKey="fl" name="Forward Link" stroke="#3b82f6" strokeWidth={3} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                    <h3 className="font-bold mb-6 flex items-center gap-2 text-slate-700">
                      <BarChart3 size={18} className="text-emerald-600" /> Top Consumo por Remota (MB)
                    </h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={usageData} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                          <XAxis type="number" fontSize={10} hide />
                          <YAxis type="category" dataKey="name" fontSize={9} width={120} axisLine={false} />
                          <Tooltip cursor={{fill: '#f8fafc'}} />
                          <Bar dataKey="in" name="Inbound" fill="#10b981" radius={[0, 4, 4, 0]} />
                          <Bar dataKey="out" name="Outbound" fill="#94a3b8" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-50 flex justify-between items-center">
                  <h2 className="text-lg font-bold">Diagnóstico de Red</h2>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                    <input 
                      type="text"
                      placeholder="Buscar remota..."
                      className="pl-9 pr-4 py-2 bg-gray-50 border-none rounded-xl text-sm w-64 focus:ring-2 focus:ring-blue-500"
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <table className="w-full text-left">
                  <thead className="bg-gray-50 text-[10px] uppercase font-black text-gray-400">
                    <tr>
                      <th className="px-6 py-4">Remota</th>
                      <th className="px-6 py-4 text-center">Eb/No RL Avg</th>
                      <th className="px-6 py-4 text-center">Eb/No FL Avg</th>
                      <th className="px-6 py-4">Estado de Enlace</th>
                      <th className="px-6 py-4">Recomendación</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {healthStats.map((site, idx) => (
                      <tr key={idx} className="hover:bg-blue-50/30 transition-colors">
                        <td className="px-6 py-4 font-bold">{site.name}</td>
                        <td className="px-6 py-4 text-center font-mono">{site.avgRL.toFixed(2)}</td>
                        <td className="px-6 py-4 text-center font-mono">{site.avgFL.toFixed(2)}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-black ${
                            site.status === 'Crítico' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                          }`}>
                            {site.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 italic">
                          {site.avgRL < 9.5 ? 'Requiere peaking antena' : 'Niveles operativos normales'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
