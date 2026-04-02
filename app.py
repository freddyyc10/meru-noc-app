import React, { useState, useMemo, useEffect } from 'react';
import { 
  Satellite, Activity, AlertTriangle, Zap, ShieldCheck, 
  Terminal, SignalHigh, Database, Wifi, Search, BarChart3
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';

// Datos simulados basados en reportes de red
const PERFORMANCE_DATA = [
  { time: '00:00', ebno: 14.2, traffic: 400 },
  { time: '04:00', ebno: 14.8, traffic: 300 },
  { time: '08:00', ebno: 15.1, traffic: 800 },
  { time: '12:00', ebno: 13.9, traffic: 1200 },
  { time: '16:00', ebno: 14.5, traffic: 950 },
  { time: '20:00', ebno: 15.3, traffic: 600 },
  { time: '23:59', ebno: 15.0, traffic: 450 },
];

const NODES = [
  { id: 'DC72', name: 'WARAIRAREPANO', type: 'HUB', status: 'online', fl: 15.5, rl: 9.8, load: 75 },
  { id: 'MER00', name: 'OBSERVATORIO', type: 'REMOTE', status: 'online', fl: 14.9, rl: 9.2, load: 30 },
  { id: 'ZUL36', name: 'CABIMAS', type: 'REMOTE', status: 'warning', fl: 11.2, rl: 7.1, load: 85 },
  { id: 'AMA05', name: 'CAICET', type: 'REMOTE', status: 'online', fl: 15.1, rl: 9.4, load: 15 },
  { id: 'GUA19', name: 'HCHF', type: 'REMOTE', status: 'error', fl: 0.0, rl: 0.0, load: 0 },
  { id: 'FAL16', name: 'MORUY', type: 'REMOTE', status: 'online', fl: 14.7, rl: 9.1, load: 45 },
  { id: 'ARA16', name: 'VALLE MORIN', type: 'REMOTE', status: 'online', fl: 14.3, rl: 9.5, load: 22 },
];

const StatusBadge = ({ status }) => {
  const config = {
    online: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    error: "bg-rose-500/10 text-rose-400 border-rose-500/20"
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${config[status]}`}>
      {status}
    </span>
  );
};

const MetricCard = ({ title, value, unit, icon: Icon, color }) => (
  <div className="bg-[#0d1117] border border-slate-800 p-4 rounded-xl hover:border-slate-700 transition-all">
    <div className="flex justify-between items-start mb-2">
      <div className={`p-2 rounded-lg bg-${color}-500/10`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
    </div>
    <div className="text-slate-500 text-[10px] uppercase font-bold tracking-widest">{title}</div>
    <div className="flex items-baseline gap-1 mt-1">
      <span className="text-2xl font-black text-white tracking-tighter">{value}</span>
      <span className="text-slate-500 text-xs">{unit}</span>
    </div>
  </div>
);

export default function App() {
  const [search, setSearch] = useState("");
  const [logs, setLogs] = useState([
    "Sincronizando con satélite Star One D2...",
    "VNO Meru-Networks: 142 terminales detectadas.",
    "Monitoreo de Eb/No activo en tiempo real."
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      const msgs = [
        "ZUL36: Eb/No crítico detectado (11.2 dB)",
        "Respaldo automático completado en MER00",
        "Tráfico inusual detectado en HUB-DC72",
        "GUA19: Reintentando handshake..."
      ];
      setLogs(prev => [msgs[Math.floor(Math.random() * msgs.length)], ...prev.slice(0, 4)]);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const filteredNodes = useMemo(() => 
    NODES.filter(n => n.name.toLowerCase().includes(search.toLowerCase()) || n.id.toLowerCase().includes(search.toLowerCase())),
    [search]
  );

  return (
    <div className="min-h-screen bg-[#010409] text-slate-300 p-4 font-sans">
      {/* Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-3">
          <div className="bg-sky-500 p-2 rounded-lg shadow-lg shadow-sky-500/20">
            <Satellite className="text-slate-900 w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tighter text-white italic">MERU NOC</h1>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Global Operations Center</p>
            </div>
          </div>
        </div>
        
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            type="text"
            placeholder="Buscar terminal..."
            className="w-full bg-[#0d1117] border border-slate-800 rounded-lg py-2 pl-10 pr-4 text-xs focus:outline-none focus:border-sky-500"
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* KPI Grid */}
        <div className="lg:col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Disponibilidad" value="99.2" unit="%" icon={ShieldCheck} color="emerald" />
          <MetricCard title="Promedio Eb/No" value="14.6" unit="dB" icon={SignalHigh} color="sky" />
          <MetricCard title="Latencia" value="580" unit="ms" icon={Activity} color="amber" />
          <MetricCard title="Ancho de Banda" value="1.2" unit="Gbps" icon={Zap} color="indigo" />
        </div>

        {/* Chart Section */}
        <div className="lg:col-span-8 bg-[#0d1117] border border-slate-800 rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-sky-400" /> Rendimiento de Enlace (24h)
            </h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={PERFORMANCE_DATA}>
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="time" stroke="#475569" fontSize={10} axisLine={false} tickLine={false} />
                <YAxis stroke="#475569" fontSize={10} axisLine={false} tickLine={false} domain={[10, 18]} />
                <Tooltip contentStyle={{backgroundColor: '#0d1117', border: '1px solid #334155'}} />
                <Area type="monotone" dataKey="ebno" stroke="#0ea5e9" strokeWidth={2} fill="url(#grad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Terminal */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-black border border-slate-800 rounded-2xl p-4 font-mono text-[10px] flex-1">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-900">
              <Terminal className="w-3 h-3 text-emerald-500" />
              <span className="text-slate-500 uppercase font-bold tracking-tighter">Live_Console_v2</span>
            </div>
            <div className="space-y-2">
              {logs.map((log, i) => (
                <div key={i} className="flex gap-2">
                  <span className="text-emerald-500/50">[{new Date().toLocaleTimeString()}]</span>
                  <span className={i === 0 ? "text-emerald-400" : "text-slate-400"}>{log}</span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-rose-500/5 border border-rose-500/20 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <span className="text-xs font-bold text-rose-500 uppercase">Alertas Activas</span>
            </div>
            <p className="text-[11px] text-slate-400 italic">No se detectan fallos masivos. GUA19 requiere intervención técnica en sitio.</p>
          </div>
        </div>

        {/* Inventory Table */}
        <div className="lg:col-span-12 bg-[#0d1117] border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-900/20 flex justify-between items-center">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-400" /> Estado por Terminal
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-[10px] font-black text-slate-500 uppercase tracking-widest border-b border-slate-800 bg-black/20">
                  <th className="px-6 py-4">Estación</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4">Eb/No (FL)</th>
                  <th className="px-6 py-4">Eb/No (RL)</th>
                  <th className="px-6 py-4">Carga CPU</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredNodes.map(node => (
                  <tr key={node.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-white text-xs">{node.id}_{node.name}</div>
                      <div className="text-[9px] text-slate-500 font-mono">{node.type}</div>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={node.status} />
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{node.fl > 0 ? `${node.fl} dB` : '--'}</td>
                    <td className="px-6 py-4 font-mono text-xs">{node.rl > 0 ? `${node.rl} dB` : '--'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1 bg-slate-800 rounded-full overflow-hidden min-w-[60px]">
                          <div 
                            className={`h-full rounded-full ${node.load > 80 ? 'bg-rose-500' : 'bg-sky-500'}`} 
                            style={{ width: `${node.load}%` }} 
                          />
                        </div>
                        <span className="text-[10px] font-bold">{node.load}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
