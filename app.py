import React, { useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell, AreaChart, Area
} from 'recharts';
import { 
  Activity, Database, Network, ShieldAlert, 
  ArrowUpCircle, ArrowDownCircle, FileUp, Info, Search
} from 'lucide-react';

const App = () => {
  const [ebnoData, setEbnoData] = useState([]);
  const [usageData, setUsageData] = useState([]);
  const [activeTab, setActiveTab] = useState('ebno');
  const [selectedStation, setSelectedStation] = useState('AMA05_CAICET');
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

      // Limpiar encabezados quitando comillas
      const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
      
      // Extraer nombres únicos de estaciones de los encabezados
      const stations = [...new Set(headers
        .filter(h => h.includes('/'))
        .map(h => h.split('/')[0])
      )];
      setAvailableStations(stations);

      const parsed = lines.slice(1).map(line => {
        const values = line.split(',');
        const row = { time: values[0].replace(/"/g, '').split(' ')[1] || '00:00' };
        
        headers.forEach((h, i) => {
          if (h.includes('/')) {
            const [station, type] = h.split('/');
            if (!row[station]) row[station] = {};
            // Simplificar nombres de métricas para el gráfico
            const key = type.includes('RL') ? 'RL' : 'FL';
            row[station][key] = parseFloat(values[i]) || null;
          }
        });
        return row;
      }).filter(r => r[selectedStation]?.RL !== null);

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
      const dataLine = lines[lines.length - 1]; // Totales al final
      
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

      setUsageData(stats.sort((a, b) => b.total - a.total).slice(0, 12));
    };
    reader.readAsText(file);
  };

  const currentMetrics = useMemo(() => {
    if (!ebnoData.length) return { rl: 0, fl: 0, status: 'N/A' };
    const last = ebnoData[ebnoData.length - 1][selectedStation];
    return {
      rl: last?.RL?.toFixed(2) || '0.00',
      fl: last?.FL?.toFixed(2) || '0.00',
      isLow: last?.RL < 9.5
    };
  }, [ebnoData, selectedStation]);

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Top Bar */}
      <nav className="bg-[#0f172a] text-white px-6 py-4 flex justify-between items-center shadow-xl border-b border-blue-500/20">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600 p-2 rounded-lg"><Network size={22} /></div>
          <div>
            <h1 className="font-black tracking-tighter text-lg uppercase">Meru NOC Analyzer</h1>
            <p className="text-[10px] font-mono text-blue-400">MONITORING SYSTEM V2.0</p>
          </div>
        </div>
        
        <div className="flex bg-slate-800 rounded-full p-1 border border-slate-700">
          <button 
            onClick={() => setActiveTab('ebno')}
            className={`px-6 py-1.5 rounded-full text-xs font-bold transition-all ${activeTab === 'ebno' ? 'bg-blue-600' : 'text-slate-400'}`}
          >
            NIVELES EB/NO
          </button>
          <button 
            onClick={() => setActiveTab('usage')}
            className={`px-6 py-1.5 rounded-full text-xs font-bold transition-all ${activeTab === 'usage' ? 'bg-blue-600' : 'text-slate-400'}`}
          >
            CONSUMO DATA
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Upload Area */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="flex flex-col items-center justify-center p-6 bg-white border-2 border-dashed border-slate-200 rounded-2xl hover:border-blue-500 cursor-pointer transition-all group">
            <FileUp className="mb-2 text-slate-400 group-hover:text-blue-500" />
            <span className="text-sm font-bold text-slate-600">Statistics (44).csv</span>
            <input type="file" className="hidden" onChange={handleEbNoFile} accept=".csv" />
          </label>
          <label className="flex flex-col items-center justify-center p-6 bg-white border-2 border-dashed border-slate-200 rounded-2xl hover:border-emerald-500 cursor-pointer transition-all group">
            <Database className="mb-2 text-slate-400 group-hover:text-emerald-500" />
            <span className="text-sm font-bold text-slate-600">Usage Report (20).csv</span>
            <input type="file" className="hidden" onChange={handleUsageFile} accept=".csv" />
          </label>
        </div>

        {ebnoData.length > 0 && activeTab === 'ebno' && (
          <div className="animate-in fade-in slide-in-from-top-4 duration-500">
            {/* Station Selector */}
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 mb-6 flex items-center gap-4">
              <Search size={18} className="text-slate-400" />
              <select 
                value={selectedStation} 
                onChange={(e) => setSelectedStation(e.target.value)}
                className="bg-transparent font-bold text-slate-700 outline-none w-full cursor-pointer"
              >
                {availableStations.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 border-l-4 border-l-red-500">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Return Link (RL)</p>
                <h2 className={`text-4xl font-black mt-2 ${currentMetrics.isLow ? 'text-red-600' : 'text-slate-900'}`}>
                  {currentMetrics.rl} <span className="text-sm font-normal text-slate-400">dB</span>
                </h2>
                {currentMetrics.isLow && (
                  <div className="mt-4 flex items-center gap-2 text-red-600 font-bold text-[10px] uppercase bg-red-50 p-2 rounded-lg">
                    <ShieldAlert size={14} /> Señal Bajo el Umbral (9.5dB)
                  </div>
                )}
              </div>
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 border-l-4 border-l-blue-500">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Forward Link (FL)</p>
                <h2 className="text-4xl font-black mt-2 text-slate-900">
                  {currentMetrics.fl} <span className="text-sm font-normal text-slate-400">dB</span>
                </h2>
              </div>
              <div className="bg-slate-900 p-6 rounded-3xl shadow-xl text-white flex flex-col justify-center">
                <p className="text-blue-400 text-[10px] font-black uppercase mb-2">Diagnóstico Automático</p>
                <p className="text-sm font-medium leading-relaxed">
                  {currentMetrics.isLow 
                    ? "Se recomienda revisión de apuntamiento o inspección de conectores en sitio debido a Eb/No degradado."
                    : "El enlace se encuentra operando en parámetros nominales de diseño."}
                </p>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 h-[450px]">
              <h3 className="font-bold text-slate-700 mb-6 flex items-center gap-2">
                <Activity size={18} className="text-blue-600" /> HISTÓRICO DE SEÑAL - {selectedStation}
              </h3>
              <ResponsiveContainer width="100%" height="100%">
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
                  <XAxis dataKey="time" fontSize={10} tickLine={false} axisLine={false} dy={10} interval="preserveStartEnd" />
                  <YAxis domain={[0, 20]} fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', fontSize: '12px' }}
                  />
                  <Legend iconType="circle" />
                  <Area 
                    type="monotone" 
                    dataKey={`${selectedStation}.RL`} 
                    name="Return Link" 
                    stroke="#ef4444" 
                    strokeWidth={3} 
                    fillOpacity={1} 
                    fill="url(#colorRL)" 
                  />
                  <Area 
                    type="monotone" 
                    dataKey={`${selectedStation}.FL`} 
                    name="Forward Link" 
                    stroke="#3b82f6" 
                    strokeWidth={3} 
                    fillOpacity={1} 
                    fill="url(#colorFL)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {usageData.length > 0 && activeTab === 'usage' && (
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 animate-in fade-in duration-500">
            <h3 className="font-bold text-slate-700 mb-8 flex items-center gap-2">
              <Database size={18} className="text-emerald-600" /> TOP 12 ESTACIONES POR CONSUMO (MB)
            </h3>
            <div className="h-[500px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={usageData} layout="vertical" margin={{ left: 40 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" fontSize={10} width={150} tickLine={false} axisLine={false} />
                  <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="inbound" name="Subida (Inbound)" fill="#10b981" radius={[0, 4, 4, 0]} barSize={12} />
                  <Bar dataKey="outbound" name="Descarga (Outbound)" fill="#94a3b8" radius={[0, 4, 4, 0]} barSize={12} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {!ebnoData.length && !usageData.length && (
          <div className="text-center py-32 bg-white rounded-3xl border border-dashed border-slate-200">
            <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
              <Info size={32} />
            </div>
            <h2 className="text-xl font-bold text-slate-700">Sistema Listo para Procesar</h2>
            <p className="text-slate-400 text-sm mt-2">Carga los archivos exportados de iDirect para visualizar los KPIs.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
