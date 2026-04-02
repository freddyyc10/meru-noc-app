import React, { useState, useEffect, useMemo } from 'react';
import { 
  Satellite, 
  Activity, 
  AlertTriangle, 
  Zap, 
  ShieldCheck, 
  Terminal, 
  Globe,
  SignalHigh,
  Cpu,
  RefreshCw,
  Search,
  ChevronRight,
  Database,
  Wifi,
  Clock
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area
} from 'recharts';

// --- PROCESAMIENTO DE DATOS SIMULADOS BASADOS EN REPORTES ---
const MOCK_TIME_SERIES = [
  { date: '2026-03-01', ebno: 15.2, traffic: 450, health: 98 },
  { date: '2026-03-05', ebno: 14.8, traffic: 520, health: 97 },
  { date: '2026-03-10', ebno: 13.1, traffic: 380, health: 92 },
  { date: '2026-03-15', ebno: 15.1, traffic: 610, health: 99 },
  { date: '2026-03-20', ebno: 14.9, traffic: 590, health: 98 },
  { date: '2026-03-25', ebno: 15.5, traffic: 750, health: 99 },
  { date: '2026-03-31', ebno: 15.3, traffic: 680, health: 98 },
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
  <div className="bg-[#0d1117] border border-slate-800 p-4 rounded-xl shadow-xl hover:border-slate-700 transition-all group">
    <div className="flex justify-between items-start mb-3">
      <div className={`p-2 rounded-lg bg-${color}-500/10 group-hover:scale-110 transition-transform`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      {trend && (
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${trend > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {trend > 0 ? '+' : ''}{trend}%
        </span>
      )}
    </div>
    <div className="text-slate-500 text-[10px] uppercase font-bold tracking-[0.15em] mb-1">{title}</div>
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
      "ZUL36: Eb/No fluctuations detected (Atmospheric).",
      "GUA19: Heartbeat timeout. Triggering alert.",
      "Traffic: Peak consumption at DC72 (4.2 Gbps).",
      "System: Auto-backup successful.",
      "Optimizing MODCOD for remote MER00..."
    ];
    const interval = setInterval(() => {
      setLogs(prev => [...prev.slice(-6), `> ${messages[Math.floor(Math.random() * messages.length)]}`]);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black/80 border border-slate-800 rounded-xl overflow-hidden font-mono flex flex-col h-full shadow-2xl">
      <div className="bg-slate-900/80 px-3 py-2 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Terminal className="w-3 h-3 text-sky-400" />
          <span className="text-[9px] text-slate-400 font-bold tracking-widest uppercase">NOC_Live_Diagnostics</span>
        </div>
      </div>
      <div className="p-4 text-[10px] space-y-1.5 text-sky-400/90 overflow-hidden">
        {logs.map((log, i) => (
          <div key={i} className={i === logs.length - 1 ? "animate-pulse flex items-start gap-2" : "flex items-start gap-2"}>
            <span className="text-slate-600">[{new Date().toLocaleTimeString([], {hour12:false})}]</span>
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
    <div className="min-h-screen bg-[#010409] text-slate-300 font-sans selection:bg-sky-500/30">
      <nav className="border-b border-slate-800 bg-[#0d1117]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-sky-500 p-1.5 rounded-lg">
              <Satellite className="text-slate-950 w-5 h-5" />
            </div>
            <h1 className="text-lg font-black tracking-tighter text-white italic">
              MERU <span className="text-sky-500 not-italic">NETWORKS</span>
            </h1>
          </div>
          <div className="hidden md:flex items-center gap-2 bg-black/40 border border-slate-800 rounded-full px-3 py-1">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_#10b981]" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Global Status: Nominal</span>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Network Uptime" value="97.8" unit="%" trend={0.4} icon={ShieldCheck} color="emerald" />
          <StatCard title="Avg FL Eb/No" value="15.1" unit="dB" trend={-1.2} icon={SignalHigh} color="sky" />
          <StatCard title="Total Traffic" value="2.84" unit="TB" trend={12.5} icon={Zap} color="amber" />
          <StatCard title="Active Nodes" value="142" unit="Units" trend={2} icon={Wifi} color="indigo" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8 bg-[#0d1117] border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="mb-8">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                <Activity className="w-4 h-4 text-sky-400" /> Rendimiento de Red (Marzo 2026)
              </h3>
            </div>
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={MOCK_TIME_SERIES}>
                  <defs>
                    <linearGradient id="gradEbNo" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="date" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis yAxisId="left" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={[12, 17]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #334155', borderRadius: '8px' }}
                  />
                  <Area yAxisId="left" type="monotone" dataKey="ebno" stroke="#0ea5e9" strokeWidth={3} fill="url(#gradEbNo)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="flex-1 min-h-[200px]">
              <TerminalLog />
            </div>
            <div className="bg-[#0d1117] border border-slate-800 rounded-2xl p-5 shadow-xl">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-500" /> Incidentes
              </h3>
              <div className="space-y-3 text-[10px]">
                <div className="p-3 bg-rose-500/5 border border-rose-500/10 rounded-xl">
                  <div className="font-bold text-rose-400">OUTAGE: GUA19_HCHF</div>
                  <div className="text-slate-500 mt-1">Falla de suministro detectada.</div>
                </div>
                <div className="p-3 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                  <div className="font-bold text-amber-400">DEGRADACIÓN: ZUL36</div>
                  <div className="text-slate-500 mt-1">Eb/No marginal por clima.</div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-12 bg-[#0d1117] border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-900/20">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <Database className="w-4 h-4 text-emerald-400" /> Telemetría de Terminales
              </h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Buscar..." 
                  className="bg-black/40 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-[11px] focus:outline-none focus:border-sky-500"
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-900/40 text-[10px] font-black text-slate-500 uppercase tracking-widest border-b border-slate-800">
                    <th className="px-6 py-4">ID / Nodo</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-center">FL (dB)</th>
                    <th className="px-6 py-4 text-center">RL (dB)</th>
                    <th className="px-6 py-4 text-right">Tráfico</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filteredNodes.map(node => (
                    <tr key={node.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-white text-xs">{node.id}_{node.name}</div>
                        <div className="text-[9px] text-slate-500 font-mono tracking-widest uppercase">{node.type}</div>
                      </td>
                      <td className="px-6 py-4"><Badge status={node.status} /></td>
                      <td className="px-6 py-4 text-center font-mono text-xs">{node.fl.toFixed(1)}</td>
                      <td className="px-6 py-4 text-center font-mono text-xs">{node.rl.toFixed(1)}</td>
                      <td className="px-6 py-4 text-right font-bold text-xs">{node.traffic}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto py-8 text-center text-[10px] text-slate-600 font-mono uppercase tracking-[0.2em]">
        Meru Networks // Integrated NOC Intelligence // 2026
      </footer>
    </div>
  );
}
