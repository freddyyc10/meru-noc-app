import React, { useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';
import { 
  Activity, Database, Network, ShieldAlert, 
  ArrowUpCircle, ArrowDownCircle, FileUp, Info
} from 'lucide-react';

const App = () => {
  const [ebnoData, setEbnoData] = useState([]);
  const [usageData, setUsageData] = useState([]);
  const [activeTab, setActiveTab] = useState('ebno');
  const [fileName, setFileName] = useState({ ebno: '', usage: '' });

  // Procesar archivo de Eb/No (Statistics 44)
  const handleEbNoFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(prev => ({ ...prev, ebno: file.name }));

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').filter(l => l.trim() !== '');
      if (lines.length < 2) return;

      const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
      
      // Mapear datos (limitamos a los últimos 100 registros para fluidez)
      const parsed = lines.slice(1).slice(-100).map(line => {
        const values = line.split(',');
        const time = values[0].replace(/"/g, '').split(' ')[1] || '00:00';
        
        // Buscamos columnas de AMA05_CAICET como referencia
        const rlIdx = headers.findIndex(h => h.includes('AMA05_CAICET/RL'));
        const flIdx = headers.findIndex(h => h.includes('AMA05_CAICET/FL'));

        return {
          time,
          rl: parseFloat(values[rlIdx]) || null,
          fl: parseFloat(values[flIdx]) || null
        };
      }).filter(d => d.rl !== null);

      setEbnoData(parsed);
    };
    reader.readAsText(file);
  };

  // Procesar archivo de Consumo (Usage Report 20)
  const handleUsageFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(prev => ({ ...prev, usage: file.name }));

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n').filter(l => l.trim() !== '');
      
      // El reporte 20 suele tener encabezados en la línea 4 (index 3)
      const headerLine = lines.find(l => l.includes('In') && l.includes('Out'));
      const dataLine = lines[lines.length - 1]; // Última línea con totales
      
      if (!headerLine || !dataLine) return;

      const headers = headerLine.split(',').map(h => h.replace(/"/g, '').trim());
      const values = dataLine.split(',');

      const stations = [];
      headers.forEach((h, i) => {
        if (h.endsWith(' In')) {
          const name = h.replace(' In', '');
          const inVal = parseFloat(values[i]) || 0;
          const outVal = parseFloat(values[i+1]) || 0;
          if (inVal > 0 || outVal > 0) {
            stations.push({ name, inbound: inVal, outbound: outVal, total: inVal + outVal });
          }
        }
      });

      setUsageData(stations.sort((a, b) => b.total - a.total).slice(0, 15));
    };
    reader.readAsText(file);
  };

  const currentStats = useMemo(() => {
    if (ebnoData.length === 0) return { rl: 0, fl: 0, status: 'N/A' };
    const last = ebnoData[ebnoData.length - 1];
    return {
      rl: last.rl?.toFixed(1),
      fl: last.fl?.toFixed(1),
      status: last.rl < 9.5 ? 'Crítico' : 'Estable'
    };
  }, [ebnoData]);

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900">
      {/* Header Estilo NOC */}
      <header className="bg-[#0f172a] text-white p-4 shadow-lg border-b border-blue-500/30">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg shadow-inner">
              <Network size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight uppercase">VNO Meru Networks</h1>
              <p className="text-[10px] text-blue-400 font-mono">NETWORK OPERATIONS CENTER - DASHBOARD v2.5</p>
            </div>
          </div>
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700">
            <button 
              onClick={() => setActiveTab('ebno')}
              className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab === 'ebno' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              NIVELES EB/NO
            </button>
            <button 
              onClick={() => setActiveTab('usage')}
              className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${activeTab === 'usage' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              TRÁFICO DATA
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Dropzones de Archivos */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="relative flex flex-col items-center p-6 bg-white border-2 border-dashed border-slate-200 rounded-2xl hover:border-blue-500 transition-colors cursor-pointer group">
            <input type="file" className="hidden" onChange={handleEbNoFile} accept=".csv" />
            <FileUp className="text-slate-400 group-hover:text-blue-500 mb-2" />
            <span className="text-sm font-bold text-slate-600">Cargar Statistics (44)</span>
            <span className="text-[10px] text-slate-400 font-mono mt-1">{fileName.ebno || 'Formato: CSV de Eb/No'}</span>
          </label>

          <label className="relative flex flex-col items-center p-6 bg-white border-2 border-dashed border-slate-200 rounded-2xl hover:border-emerald-500 transition-colors cursor-pointer group">
            <input type="file" className="hidden" onChange={handleUsageFile} accept=".csv" />
            <FileUp className="text-slate-400 group-hover:text-emerald-500 mb-2" />
            <span className="text-sm font-bold text-slate-600">Cargar Usage Report (20)</span>
            <span className="text-[10px] text-slate-400 font-mono mt-1">{fileName.usage || 'Formato: CSV de Tráfico'}</span>
          </label>
        </div>

        {ebnoData.length === 0 && usageData.length === 0 ? (
          <div className="text-center py-24 bg-white rounded-3xl border border-slate-100">
            <div className="animate-bounce mb-4 inline-block p-4 bg-blue-50 rounded-full text-blue-600">
              <Info size={32} />
            </div>
            <h2 className="text-lg font-bold text-slate-700">Esperando Datos...</h2>
            <p className="text-slate-400 text-sm max-w-xs mx-auto">Sube los archivos CSV exportados de la iDirect para iniciar el análisis.</p>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {activeTab === 'ebno' ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 text-red-600"><ArrowDownCircle size={48} /></div>
                    <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Eb/No RL Actual</p>
                    <p className={`text-4xl font-black mt-1 ${currentStats.rl < 9.5 ? 'text-red-600' : 'text-slate-900'}`}>{currentStats.rl} dB</p>
                    <div className="mt-4 flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${currentStats.rl < 9.5 ? 'bg-red-500 animate-ping' : 'bg-emerald-500'}`}></span>
                      <span className="text-[10px] font-bold uppercase">{currentStats.status}</span>
                    </div>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 text-blue-600"><ArrowUpCircle size={48} /></div>
                    <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Eb/No FL Actual</p>
                    <p className="text-4xl font-black mt-1 text-slate-900">{currentStats.fl} dB</p>
                    <p className="mt-4 text-[10px] font-bold text-blue-600 uppercase tracking-tighter">Lectura de Telemetría Ok</p>
                  </div>
                  <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center bg-slate-900 text-white">
                    <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-2">Recomendación NOC</h4>
                    <p className="text-sm font-medium">
                      {currentStats.rl < 9.5 
                        ? 'ALERTA: Se detecta degradación en el Return Link. Posible desapuntamiento o condiciones climáticas en sitio.' 
                        : 'SISTEMA OPERATIVO: Los niveles de señal se encuentran dentro del rango de diseño (Eb/No > 9.5 dB).'}
                    </p>
                  </div>
                </div>

                <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-lg font-black flex items-center gap-2">
                      <Activity className="text-blue-600" size={20} /> COMPORTAMIENTO DE ENLACE (TIEMPO REAL)
                    </h3>
                  </div>
                  <div className="h-96 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={ebnoData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="time" fontSize={10} axisLine={false} tickLine={false} dy={10} />
                        <YAxis domain={[0, 20]} fontSize={10} axisLine={false} tickLine={false} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff', fontSize: '12px' }}
                          itemStyle={{ color: '#fff' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '10px', fontWeight: 'bold', paddingTop: '20px' }} />
                        <Line type="monotone" dataKey="rl" name="Return Link (Eb/No)" stroke="#ef4444" strokeWidth={4} dot={false} animationDuration={1500} />
                        <Line type="monotone" dataKey="fl" name="Forward Link (Eb/No)" stroke="#3b82f6" strokeWidth={4} dot={false} animationDuration={1500} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100">
                <h3 className="text-lg font-black flex items-center gap-2 mb-8">
                  <Database className="text-emerald-600" size={20} /> CONSUMO AGREGADO POR ESTACIÓN (MB)
                </h3>
                <div className="h-[600px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={usageData} layout="vertical" margin={{ left: 40, right: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                      <XAxis type="number" fontSize={10} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="name" fontSize={9} axisLine={false} tickLine={false} width={150} />
                      <Tooltip 
                        cursor={{fill: '#f8fafc'}}
                        contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '12px', color: '#fff' }}
                      />
                      <Legend />
                      <Bar dataKey="inbound" name="Data Inbound" fill="#10b981" radius={[0, 4, 4, 0]} />
                      <Bar dataKey="outbound" name="Data Outbound" fill="#94a3b8" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
      
      <footer className="max-w-7xl mx-auto p-6 text-center text-slate-400 text-[10px] font-bold tracking-widest uppercase">
        © 2024 VNO MERU NETWORKS | Herramienta de Diagnóstico Interno
      </footer>
    </div>
  );
};

export default App;
