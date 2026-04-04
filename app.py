import React, { useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, AreaChart, Area, Cell
} from 'recharts';
import { 
  Activity, Database, Network, ShieldAlert, 
  FileUp, Info, Search, ChevronRight, Signal
} from 'lucide-react';

const App = () => {
  const [ebnoData, setEbnoData] = useState([]);
  const [usageData, setUsageData] = useState([]);
  const [activeTab, setActiveTab] = useState('ebno');
  const [selectedStation, setSelectedStation] = useState('');
  const [availableStations, setAvailableStations] = useState([]);

  // Procesar archivo de Eb/No (statistics 44)
  const handleEbNoFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').map(l => l.trim()).filter(l => l !== '');
      if (lines.length < 2) return;

      const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
      
      const stations = [...new Set(headers
        .filter(h => h.includes('/'))
        .map(h => h.split('/')[0])
      )].sort();
      
      setAvailableStations(stations);
      if (stations.length > 0 && !selectedStation) setSelectedStation(stations[0]);

      const parsed = lines.slice(1).map(line => {
        const values = line.split(',');
        const timePart = values[0]?.replace(/"/g, '').split(' ')[1] || '00:00';
        const row = { time: timePart.substring(0, 5) }; // HH:mm
        
        headers.forEach((h, i) => {
          if (h.includes('/')) {
            const [station, type] = h.split('/');
            if (!row[station]) row[station] = {};
            const val = parseFloat(values[i]);
            const key = type.toLowerCase().includes('rl') ? 'RL' : 'FL';
            row[station][key] = isNaN(val) ? null : val;
          }
        });
        return row;
      }).filter(r => r.time);

      setEbnoData(parsed);
    };
    reader.readAsText(file);
  };

  // Procesar archivo de Consumo (Usage Report 20)
  const handleUsageFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').filter(l => l.trim() !== '');
      const headerLine = lines.find(l => l.includes('In') && l.includes('Out'));
      const dataLine = lines[lines.length - 1]; 
      
      if (!headerLine || !dataLine) return;

      const headers = headerLine.split(',').map(h => h.replace(/"/g, '').trim());
      const values = dataLine.split(',');

      const stats = [];
      headers.forEach((h, i) => {
        if (h.endsWith(' In')) {
          const name = h.replace(' In', '');
          const inVal = parseFloat(values[i]) || 0;
          const outVal = parseFloat(values[i+1]) || 0;
          if (inVal > 0 || outVal > 0) {
            stats.push({ name, inbound: inVal, outbound: outVal, total: inVal + outVal });
          }
        }
      });

      setUsageData(stats.sort((a, b) => b.total - a.total).slice(0, 15));
    };
    reader.readAsText(file);
  };

  const currentMetrics = useMemo(() => {
    if (!ebnoData.length || !selectedStation) return null;
    
    // Buscar el último registro que tenga datos válidos para la estación seleccionada
    const validData = ebnoData.filter(d => d[selectedStation]?.RL !== null || d[selectedStation]?.FL !== null);
    if (!validData.length) return null;
    
    const last = validData[validData.length - 1][selectedStation];
    return {
      rl: last?.RL || 0,
      fl: last?.FL || 0,
      isLow: last?.RL !== null && last?.RL < 9.5
    };
  }, [ebnoData, selectedStation]);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* Header Estilo NOC */}
      <header className="bg-[#0f172a] text-white p-4 shadow-2xl border-b border-blue-500/30">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-500/20">
              <Network size={24} strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight uppercase">VNO Meru Analytics</h1>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">Live Dashboard v2.5</span>
              </div>
            </div>
          </div>

          <div className="flex bg-slate-800/50 p-1 rounded-xl border border-slate-700">
            <button 
              onClick={() => setActiveTab('ebno')}
              className={`px-5 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'ebno' ? 'bg-blue-600 shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              NIVELES EB/NO
            </button>
            <button 
              onClick={() => setActiveTab('usage')}
              className={`px-5 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'usage' ? 'bg-blue-600 shadow-lg' : 'text-slate-400 hover:text-white'}`}
            >
              TRÁFICO VNO
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Controles de Carga */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="group relative flex flex-col items-center justify-center p-8 bg-white border-2 border-dashed border-slate-200 rounded-3xl hover:border-blue-500 hover:bg-blue-50/30 transition-all cursor-pointer">
            <FileUp className="mb-3 text-slate-400 group-hover:text-blue-600 transition-colors" size={32} />
            <span className="text-sm font-bold text-slate-600">Statistics (Niveles Eb/No)</span>
            <p className="text-[10px] text-slate-400 mt-1">Arrastra aquí el archivo .csv</p>
            <input type="file" className="hidden" onChange={handleEbNoFile} accept=".csv" />
          </label>
          <label className="group relative flex flex-col items-center justify-center p-8 bg-white border-2 border-dashed border-slate-200 rounded-3xl hover:border-emerald-500 hover:bg-emerald-50/30 transition-all cursor-pointer">
            <Database className="mb-3 text-slate-400 group-hover:text-emerald-600 transition-colors" size={32} />
            <span className="text-sm font-bold text-slate-600">Usage Report (Consumo MB)</span>
            <p className="text-[10px] text-slate-400 mt-1">Arrastra aquí el reporte de tráfico</p>
            <input type="file" className="hidden" onChange={handleUsageFile} accept=".csv" />
          </label>
        </div>

        {activeTab === 'ebno' && ebnoData.length > 0 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Selector de Estación */}
            <div className="bg-white p-5 rounded-3xl shadow-sm border border-slate-100 flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2 text-slate-400 mr-2">
                <Search size={18} />
                <span className="text-xs font-bold uppercase tracking-wider">Estación:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {availableStations.slice(0, 8).map(s => (
                  <button
                    key={s}
                    onClick={() => setSelectedStation(s)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${selectedStation === s ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-500/20' : 'bg-slate-50 text-slate-500 hover:bg-slate-100'}`}
                  >
                    {s}
                  </button>
                ))}
                <select 
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-50 text-slate-600 border-none outline-none focus:ring-2 focus:ring-blue-500/20"
                  value={selectedStation}
                  onChange={(e) => setSelectedStation(e.target.value)}
                >
                  <option value="">Más estaciones...</option>
                  {availableStations.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>

            {/* Tarjetas de Métricas */}
            {currentMetrics && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 relative overflow-hidden group">
                  <div className={`absolute top-0 left-0 w-1.5 h-full ${currentMetrics.isLow ? 'bg-red-500' : 'bg-blue-500'}`} />
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Return Link (RL)</p>
                  <div className="flex items-baseline gap-2">
                    <h2 className={`text-5xl font-black tracking-tighter ${currentMetrics.isLow ? 'text-red-600' : 'text-slate-900'}`}>
                      {currentMetrics.rl.toFixed(1)}
                    </h2>
                    <span className="text-slate-400 font-bold uppercase text-xs">dB</span>
                  </div>
                  {currentMetrics.isLow && (
                    <div className="mt-4 flex items-center gap-2 text-red-600 font-bold text-[10px] bg-red-50 p-2 rounded-lg">
                      <ShieldAlert size={14} /> ALERTA: SEÑAL DEGRADADA
                    </div>
                  )}
                </div>

                <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1.5 h-full bg-emerald-500" />
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Forward Link (FL)</p>
                  <div className="flex items-baseline gap-2">
                    <h2 className="text-5xl font-black tracking-tighter text-slate-900">
                      {currentMetrics.fl.toFixed(1)}
                    </h2>
                    <span className="text-slate-400 font-bold uppercase text-xs">dB</span>
                  </div>
                </div>

                <div className="bg-slate-900 p-6 rounded-[2rem] shadow-xl text-white flex flex-col justify-center relative overflow-hidden">
                  <Activity className="absolute right-[-20px] bottom-[-20px] text-white/5 w-40 h-40" />
                  <div className="relative z-10">
                    <p className="text-blue-400 text-[10px] font-black uppercase tracking-widest mb-2">Estado del Enlace</p>
                    <p className="text-sm font-medium leading-relaxed">
                      {currentMetrics.isLow 
                        ? `La estación ${selectedStation} requiere revisión técnica inmediata por niveles fuera de norma.` 
                        : "El enlace satelital opera correctamente con margen de desvanecimiento estable."}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Gráfica de Eb/No */}
            <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 h-[500px]">
              <div className="flex justify-between items-center mb-8">
                <h3 className="font-bold text-slate-800 flex items-center gap-3 italic">
                  <Signal size={20} className="text-blue-600" /> TRENDING: {selectedStation}
                </h3>
                <div className="flex gap-4 text-[10px] font-bold">
                  <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-blue-500"></span> FL TUNER</span>
                  <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500"></span> RL MEASURED</span>
                </div>
              </div>
              <ResponsiveContainer width="100%" height="90%">
                <AreaChart data={ebnoData}>
                  <defs>
                    <linearGradient id="colorRL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorFL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="time" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={false} 
                    interval="preserveStartEnd" 
                    minTickGap={50}
                  />
                  <YAxis domain={[5, 20]} fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', fontSize: '11px', fontWeight: 'bold' }}
                    labelClassName="text-slate-400"
                  />
                  <Area 
                    type="monotone" 
                    dataKey={`${selectedStation}.RL`} 
                    name="Return Link" 
                    stroke="#ef4444" 
                    strokeWidth={3} 
                    fill="url(#colorRL)" 
                    connectNulls
                  />
                  <Area 
                    type="monotone" 
                    dataKey={`${selectedStation}.FL`} 
                    name="Forward Link" 
                    stroke="#3b82f6" 
                    strokeWidth={3} 
                    fill="url(#colorFL)" 
                    connectNulls
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'usage' && usageData.length > 0 && (
          <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 animate-in fade-in duration-500">
            <h3 className="font-bold text-slate-800 mb-8 flex items-center gap-2">
              <Database size={20} className="text-emerald-600" /> CONSUMO ACUMULADO POR REMOTA (MB)
            </h3>
            <div className="h-[600px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={usageData} layout="vertical" margin={{ left: 40, right: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" fontSize={10} width={150} tickLine={false} axisLine={false} />
                  <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', fontSize: '11px' }}
                  />
                  <Bar dataKey="inbound" name="Subida (Inbound)" fill="#10b981" stackId="a" radius={[0, 0, 0, 0]} barSize={20} />
                  <Bar dataKey="outbound" name="Descarga (Outbound)" fill="#94a3b8" stackId="a" radius={[0, 10, 10, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {!ebnoData.length && !usageData.length && (
          <div className="text-center py-40 bg-white rounded-[3rem] border-2 border-dashed border-slate-200">
            <div className="bg-slate-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 text-slate-300">
              <Info size={40} />
            </div>
            <h2 className="text-2xl font-black text-slate-800 tracking-tight">CENTRO DE DATOS MERU</h2>
            <p className="text-slate-400 text-sm mt-2 max-w-xs mx-auto font-medium">Carga los archivos .csv generados por iDirect para iniciar el análisis en tiempo real.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
