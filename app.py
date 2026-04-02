import React, { useState, useEffect, useMemo } from 'react';
import { 
  Satellite, 
  Activity, 
  AlertTriangle, 
  Zap, 
  ShieldCheck, 
  Terminal, 
  SignalHigh,
  Database,
  Wifi,
  Search
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

// Datos de ejemplo para la gráfica
const MOCK_TIME_SERIES = [
  { date: '01 Mar', ebno: 15.2 },
  { date: '05 Mar', ebno: 14.8 },
  { date: '10 Mar', ebno: 13.1 },
  { date: '15 Mar', ebno: 15.1 },
  { date: '20 Mar', ebno: 14.9 },
  { date: '25 Mar', ebno: 15.5 },
  { date: '31 Mar', ebno: 15.3 },
];

const NODE_DATA = [
  { id: 'DC72', name: 'WARAIRAREPANO', type: 'HUB-CORE', status: 'online', fl: 15.5, rl: 9.8, traffic: '1.2 TB' },
  { id: 'MER00', name: 'OBSERVATORIO', type: 'REMOTE', status: 'online', fl: 14.9, rl: 9.2, traffic: '450 GB' },
  { id: 'ZUL36', name: 'CABIMAS', type: 'REMOTE', status: 'warning', fl: 13.8, rl: 8.5, traffic: '320 GB' },
  { id: 'AMA05', name: 'CAICET', type: 'REMOTE', status: 'online', fl: 15.1, rl: 9.4, traffic: '180 GB' },
  { id: 'GUA19', name: 'HCHF', type: 'REMOTE', status: 'error', fl: 0.0, rl: 0.0, traffic: '12 GB' },
  { id: 'FAL16', name: 'MORUY', type: 'REMOTE', status: 'online', fl: 14.7, rl: 9.1, traffic: '95 GB' },
];

const Badge = ({ status }) => {
  const styles = {
    online: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    error: "bg-rose-500/10 text-rose-400 border-rose-500/20"
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-tighter border ${styles[status]}`}>
      {status}
    </span>
  );
};

const StatCard = ({ title, value, unit, trend, icon: Icon, color }) => (
  <div className="bg-[#0d1117] border border-slate-800 p-4 rounded-xl shadow-xl hover:border-slate-700 transition-all">
    <div className="flex justify-between items-start mb-3">
      <div className={`p-2 rounded-lg bg-${color}-500/10`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      {trend && (
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${trend > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {trend > 0 ? '+' : ''}{trend}%
        </span>
      )}
    </div>
    <div className="text-slate-500 text-[10px] uppercase font-bold tracking-widest mb-1">{title}</div>
    <div className="flex items-baseline gap-1">
      <span className="text-2xl font-black text-white tracking-tighter">{value}</span>
      <span className="text-slate-500 text-xs font-medium">{unit}</span>
    </div>
  </div>
);

const TerminalLog = () => {
  const [logs, setLogs] = useState([
    "Initializing Meru Intelligence Layer...",
    "VNO Segment 13: All carriers nominal.",
    "Loading metrics for March 2026..."
  ]);

  useEffect(() => {
    const messages = [
      "ZUL36: Eb/No fluctuations detected.",
      "GUA19: Heartbeat timeout. Alert triggered.",
      "Traffic: Peak at DC72 (4.2 Gbps).",
      "System: Auto-backup successful."
    ];
    const interval = setInterval(() => {
      setLogs(prev => [...prev.slice(-4), `> ${messages[Math.floor(Math.random() * messages.length)]}`]);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black border border-slate-800 rounded-xl overflow-hidden font-mono h-full">
      <div className="bg-slate-900 px-3 py-1.5 border-b border-slate-800 flex items-center gap-2">
        <Terminal className="w-3 h-3 text-sky-400" />
        <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">NOC_Live</span>
      </div>
      <div className="p-3 text-[10px] space-y-1 text-sky-400/80">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-slate-600">&gt;</span>
            <span>{log}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function App() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredNodes = useMemo(() => {
    return NODE_DATA.filter(n => 
      n.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      n.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm]);

  return (
    <div className="min-h-screen bg-[#010409] text-slate-300 font-sans p-4 md:p-8">
      {/* Header */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-sky-500 p-2 rounded-xl">
            <Satellite className="text-slate-900 w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tighter text-white italic">MERU NETWORKS</h1>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.3em]">NOC Dashboard v2.5</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 bg-emerald-500/5 border border-emerald-500/20 rounded-full px-4 py-1.5">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Sistemas Operativos</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Uptime Red" value="97.8" unit="%" trend={0.4} icon={ShieldCheck} color="emerald" />
          <StatCard title="Promedio Eb/No" value="15.1" unit="dB" trend={-1.2} icon={SignalHigh} color="sky" />
          <StatCard title="Tráfico Total" value="2.84" unit="TB" trend={12.5} icon={Zap} color="amber" />
          <StatCard title="Nodos Activos" value="142" unit="" trend={2} icon={Wifi} color="indigo" />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Chart */}
          <div className="lg:col-span-8 bg-[#0d1117] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                <Activity className="w-4 h-4 text-sky-400" /> Rendimiento de Red
              </h3>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={MOCK_TIME_SERIES}>
                  <defs>
                    <linearGradient id="colorEbNo" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="date" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={[12, 17]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="ebno" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorEbNo)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-4 space-y-6">
            <div className="h-48">
              <TerminalLog />
            </div>
            <div className="bg-[#0d1117] border border-slate-800 rounded-2xl p-5 shadow-xl">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-500" /> Alertas Críticas
              </h3>
              <div className="space-y-3">
                <div className="p-3 bg-rose-500/5 border border-rose-500/10 rounded-xl">
                  <div className="font-bold text-rose-400 text-[11px]">OUTAGE: GUA19_HCHF</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Sin respuesta desde las 02:15 UTC.</div>
                </div>
                <div className="p-3 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                  <div className="font-bold text-amber-400 text-[11px]">WARNING: ZUL36_CABIMAS</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Eb/No por debajo del umbral nominal.</div>
                </div>
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="lg:col-span-12 bg-[#0d1117] border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-900/20">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <Database className="w-4 h-4 text-emerald-400" /> Inventario de Nodos
              </h3>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Buscar nodo o ID..." 
                  className="bg-black border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-[11px] w-full focus:outline-none focus:border-sky-500 transition-colors"
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-900/40 text-[10px] font-black text-slate-500 uppercase tracking-[0.15em] border-b border-slate-800">
                    <th className="px-6 py-4">ID / Nombre</th>
                    <th className="px-6 py-4">Estado</th>
                    <th className="px-6 py-4 text-center">FL Eb/No</th>
                    <th className="px-6 py-4 text-center">RL Eb/No</th>
                    <th className="px-6 py-4 text-right">Tráfico Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filteredNodes.map(node => (
                    <tr key={node.id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="font-bold text-white text-xs group-hover:text-sky-400 transition-colors">{node.id}_{node.name}</div>
                        <div className="text-[9px] text-slate-500 font-mono uppercase mt-0.5">{node.type}</div>
                      </td>
                      <td className="px-6 py-4"><Badge status={node.status} /></td>
                      <td className="px-6 py-4 text-center font-mono text-xs">{node.fl > 0 ? node.fl.toFixed(1) : '--'}</td>
                      <td className="px-6 py-4 text-center font-mono text-xs">{node.rl > 0 ? node.rl.toFixed(1) : '--'}</td>
                      <td className="px-6 py-4 text-right font-bold text-xs text-white/80">{node.traffic}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
