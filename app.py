import React, { useState, useEffect, useMemo } from 'react';
import { 
  Satellite, 
  Activity, 
  AlertTriangle, 
  Zap, 
  ShieldCheck, 
  Terminal, 
  BarChart3, 
  Settings,
  Globe,
  SignalHigh,
  Cpu,
  RefreshCw
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
  Area,
  BarChart,
  Bar
} from 'recharts';

// --- MOCK DATA PARA LA ESTRUCTURA ---
const SATELLITE_STATS = [
  { time: '00:00', ebno_fl: 15.2, ebno_rl: 9.8, traffic: 120 },
  { time: '04:00', ebno_fl: 14.8, ebno_rl: 9.5, traffic: 80 },
  { time: '08:00', ebno_fl: 15.5, ebno_rl: 9.9, traffic: 250 },
  { time: '12:00', ebno_fl: 14.2, ebno_rl: 8.7, traffic: 410 },
  { time: '16:00', ebno_fl: 15.1, ebno_rl: 9.4, traffic: 380 },
  { time: '20:00', ebno_fl: 15.8, ebno_rl: 10.1, traffic: 210 },
];

const NODES_STATUS = [
  { id: 'ZUL36', name: 'Zulia Sur', status: 'warning', lat: 15.2, fl: 14.2 },
  { id: 'DC72', name: 'Waraira', status: 'online', lat: 9.9, fl: 15.5 },
  { id: 'AMA05', name: 'Caicet', status: 'online', lat: 9.5, fl: 15.2 },
  { id: 'MIR68', name: 'Paparo', status: 'online', lat: 9.4, fl: 14.9 },
  { id: 'GUA19', name: 'Calabozo', status: 'error', lat: 0.0, fl: 0.0 },
];

// --- COMPONENTES MODULARES ---

const StatCard = ({ title, value, unit, trend, icon: Icon, color }) => (
  <div className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl backdrop-blur-md">
    <div className="flex justify-between items-start mb-2">
      <div className={`p-2 rounded-lg bg-${color}-500/10`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      <span className={`text-xs font-bold ${trend >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
        {trend >= 0 ? '+' : ''}{trend}%
      </span>
    </div>
    <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold">{title}</div>
    <div className="flex items-baseline gap-1 mt-1">
      <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
      <span className="text-slate-500 text-sm">{unit}</span>
    </div>
  </div>
);

const TerminalAI = () => {
  const [logs, setLogs] = useState([
    "Initializing Meru Intelligence Engine v2.5...",
    "Connecting to Gemini-Flash Satellite Model...",
    "Analyzing March 2026 Telemetry Data...",
    "Ready for Diagnostic Command."
  ]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const runDiagnostic = () => {
    setIsAnalyzing(true);
    setLogs(prev => [...prev, "> Scanning ISP Link Budget..."]);
    setTimeout(() => {
      setLogs(prev => [...prev, "⚠ Alert: Eb/No fluctuations detected in Node GUA19.", "✓ Recommendation: Check BUC power levels.", "✓ Diagnostic complete."]);
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="bg-black border border-emerald-500/30 rounded-xl overflow-hidden flex flex-col h-full shadow-[0_0_20px_rgba(16,185,129,0.1)]">
      <div className="bg-emerald-500/10 px-4 py-2 border-b border-emerald-500/30 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-mono text-emerald-400 uppercase tracking-widest">Meru_AI_Terminal</span>
        </div>
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-rose-500" />
          <div className="w-2 h-2 rounded-full bg-amber-500" />
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
        </div>
      </div>
      <div className="p-4 font-mono text-[11px] flex-1 overflow-y-auto space-y-1 text-emerald-500/80">
        {logs.map((log, i) => <div key={i}>{log}</div>)}
        {isAnalyzing && <div className="animate-pulse">_ Processing telemetry...</div>}
      </div>
      <div className="p-3 bg-emerald-500/5">
        <button 
          onClick={runDiagnostic}
          disabled={isAnalyzing}
          className="w-full py-2 bg-emerald-500 text-black text-xs font-bold rounded hover:bg-emerald-400 transition-colors uppercase tracking-widest"
        >
          {isAnalyzing ? 'Analyzing...' : 'Run Global Diagnostic'}
        </button>
      </div>
    </div>
  );
};

const NodeStatusTable = () => (
  <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
    <div className="p-4 border-b border-slate-800 bg-slate-800/30">
      <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
        <Globe className="w-4 h-4 text-sky-400" /> Status de Nodos Críticos
      </h3>
    </div>
    <table className="w-full text-left text-xs">
      <thead className="bg-black/20 text-slate-500 uppercase">
        <tr>
          <th className="p-3">Nodo</th>
          <th className="p-3 text-center">RL Eb/No</th>
          <th className="p-3 text-center">FL Eb/No</th>
          <th className="p-3 text-right">Estado</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-slate-800/50">
        {NODES_STATUS.map((node) => (
          <tr key={node.id} className="hover:bg-sky-500/5 transition-colors">
            <td className="p-3 font-semibold text-slate-200">{node.id} <span className="text-[10px] text-slate-500 block font-normal">{node.name}</span></td>
            <td className="p-3 text-center font-mono text-sky-400">{node.lat} dB</td>
            <td className="p-3 text-center font-mono text-indigo-400">{node.fl} dB</td>
            <td className="p-3 text-right">
              <span className={`px-2 py-1 rounded-full text-[9px] font-bold uppercase tracking-tighter ${
                node.status === 'online' ? 'bg-emerald-500/10 text-emerald-400' : 
                node.status === 'warning' ? 'bg-amber-500/10 text-amber-400' : 'bg-rose-500/10 text-rose-400'
              }`}>
                {node.status}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

// --- COMPONENTE PRINCIPAL ---

export default function App() {
  const [activeTab, setActiveTab] = useState('ops');

  return (
    <div className="min-h-screen bg-[#05070a] text-slate-200 p-6 font-sans">
      {/* Header Estilo Centro de Comando */}
      <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4 border-b border-slate-800 pb-6">
        <div className="flex items-center gap-4">
          <div className="bg-sky-500 p-3 rounded-2xl shadow-[0_0_20px_rgba(14,165,233,0.4)]">
            <Satellite className="text-white w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">MERU <span className="text-sky-500 not-italic">NETWORKS</span></h1>
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono tracking-widest">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              SATELLITE OPS CENTER // MARCH_2026 // 02:28:45 UTC
            </div>
          </div>
        </div>

        <nav className="flex bg-slate-900 border border-slate-800 rounded-lg p-1">
          {[
            { id: 'ops', label: 'OPERACIONES', icon: Activity },
            { id: 'ia', label: 'INTELIGENCIA', icon: Cpu },
            { id: 'reports', label: 'TELEMETRÍA', icon: BarChart3 }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-xs font-bold transition-all duration-200 ${
                activeTab === tab.id 
                ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' 
                : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Grid Principal - Responsive */}
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Fila 1: Métricas Críticas */}
        <div className="lg:col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Disponibilidad Global" value="97.8" unit="%" trend={0.4} icon={ShieldCheck} color="emerald" />
          <StatCard title="Promedio FL Eb/No" value="15.1" unit="dB" trend={-1.2} icon={SignalHigh} color="sky" />
          <StatCard title="Tráfico Total Mes" value="2.4" unit="TB" trend={12.5} icon={Zap} color="indigo" />
          <StatCard title="Incidentes Críticos" value="3" unit="Activos" trend={-50} icon={AlertTriangle} color="rose" />
        </div>

        {/* Fila 2: Gráficos y Tabla */}
        <div className="lg:col-span-8 space-y-6">
          {/* Gráfico de Performance */}
          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-400" /> Monitoreo de Enlace (Eb/No)
              </h3>
              <div className="flex gap-4">
                <div className="flex items-center gap-2 text-[10px] text-sky-400 uppercase font-bold">
                  <div className="w-2 h-2 rounded-full bg-sky-500" /> Forward Link
                </div>
                <div className="flex items-center gap-2 text-[10px] text-indigo-400 uppercase font-bold">
                  <div className="w-2 h-2 rounded-full bg-indigo-500" /> Return Link
                </div>
              </div>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={SATELLITE_STATS}>
                  <defs>
                    <linearGradient id="colorFL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorRL" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="ebno_fl" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorFL)" strokeWidth={2} />
                  <Area type="monotone" dataKey="ebno_rl" stroke="#6366f1" fillOpacity={1} fill="url(#colorRL)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <NodeStatusTable />
            <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-xl relative overflow-hidden flex flex-col justify-center items-center">
              <div className="absolute top-0 right-0 p-4">
                <Settings className="w-4 h-4 text-slate-700 animate-spin-slow" />
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-sky-500/10 rounded-full flex items-center justify-center mx-auto mb-4 border border-sky-500/30">
                  <RefreshCw className="w-8 h-8 text-sky-500" />
                </div>
                <h4 className="text-slate-200 font-bold uppercase tracking-widest text-sm">Próxima Sincronización</h4>
                <p className="text-slate-500 text-[10px] mt-1 font-mono uppercase tracking-tighter">Telemetría Inbound // 00:04:12</p>
                <div className="mt-4 w-32 bg-slate-800 h-1 rounded-full mx-auto overflow-hidden">
                  <div className="bg-sky-500 h-full w-2/3 animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Barra Lateral: IA y Acciones Rápidas */}
        <div className="lg:col-span-4 space-y-6">
          <TerminalAI />
          
          <div className="bg-gradient-to-br from-indigo-900/20 to-sky-900/20 border border-indigo-500/20 p-6 rounded-xl">
            <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4" /> Acciones de Comando
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <button className="bg-slate-800 hover:bg-slate-700 p-3 rounded-lg flex flex-col items-center gap-2 transition-all border border-slate-700">
                <RefreshCw className="w-5 h-5 text-sky-400" />
                <span className="text-[10px] font-bold uppercase tracking-tighter">Reset Modem</span>
              </button>
              <button className="bg-slate-800 hover:bg-slate-700 p-3 rounded-lg flex flex-col items-center gap-2 transition-all border border-slate-700">
                <SignalHigh className="w-5 h-5 text-emerald-400" />
                <span className="text-[10px] font-bold uppercase tracking-tighter">Peaking Test</span>
              </button>
              <button className="bg-slate-800 hover:bg-slate-700 p-3 rounded-lg flex flex-col items-center gap-2 transition-all border border-slate-700">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                <span className="text-[10px] font-bold uppercase tracking-tighter">Clear Alarms</span>
              </button>
              <button className="bg-rose-500/10 hover:bg-rose-500/20 p-3 rounded-lg flex flex-col items-center gap-2 transition-all border border-rose-500/30">
                <AlertTriangle className="w-5 h-5 text-rose-500" />
                <span className="text-[10px] font-bold uppercase tracking-tighter">Panic Mode</span>
              </button>
            </div>
          </div>
        </div>

      </main>

      <style>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 8s linear infinite;
        }
      `}</style>
    </div>
  );
}
