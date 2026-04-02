import React, { useState, useEffect } from 'react';
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
  RefreshCw,
  Search,
  ChevronRight
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

// --- DATOS SIMULADOS BASADOS EN TUS REPORTES ---
const PERFORMANCE_DATA = [
  { time: '01 Mar', ebno_fl: 15.2, traffic: 120, availability: 98.2 },
  { time: '05 Mar', ebno_fl: 14.8, traffic: 150, availability: 97.5 },
  { time: '10 Mar', ebno_fl: 13.5, traffic: 180, availability: 96.8 }, // Rain Fade event
  { time: '15 Mar', ebno_fl: 15.1, traffic: 210, availability: 98.5 },
  { time: '20 Mar', ebno_fl: 14.9, traffic: 190, availability: 97.9 },
  { time: '25 Mar', ebno_fl: 15.5, traffic: 250, availability: 98.1 },
  { time: '31 Mar', ebno_fl: 15.3, traffic: 230, availability: 98.4 },
];

const NODE_LIST = [
  { id: 'DC72', name: 'WARAIRAREPANO', state: 'Distrito Capital', status: 'online', fl: 15.5, traffic: '51.3 GB' },
  { id: 'MER00', name: 'OBSERVATORIO', state: 'Mérida', status: 'online', fl: 14.8, traffic: '24.5 GB' },
  { id: 'ZUL36', name: 'SUR DEL LAGO', state: 'Zulia', status: 'warning', fl: 14.2, traffic: '18.2 GB' },
  { id: 'GUA19', name: 'CALABOZO', state: 'Guárico', status: 'error', fl: 0.0, traffic: '5.4 GB' },
  { id: 'AMA05', name: 'CAICET', state: 'Amazonas', status: 'online', fl: 15.2, traffic: '10.9 GB' },
];

// --- COMPONENTES ---

const StatCard = ({ title, value, unit, trend, icon: Icon, color }) => (
  <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl shadow-lg">
    <div className="flex justify-between items-start mb-3">
      <div className={`p-2 rounded-lg bg-${color}-500/10`}>
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${trend >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
        {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
      </span>
    </div>
    <div className="text-slate-500 text-[10px] uppercase font-bold tracking-widest">{title}</div>
    <div className="flex items-baseline gap-1 mt-1">
      <span className="text-2xl font-bold text-white tracking-tight">{value}</span>
      <span className="text-slate-500 text-xs">{unit}</span>
    </div>
  </div>
);

const NodeRow = ({ node }) => (
  <div className="group flex items-center justify-between p-3 hover:bg-slate-800/40 rounded-lg transition-all border border-transparent hover:border-slate-700">
    <div className="flex items-center gap-3">
      <div className={`w-2 h-2 rounded-full ${
        node.status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 
        node.status === 'warning' ? 'bg-amber-500 shadow-[0_0_8px_#f59e0b]' : 
        'bg-rose-500 shadow-[0_0_8px_#f43f5e]'
      }`} />
      <div>
        <div className="text-xs font-bold text-slate-200">{node.id}_{node.name}</div>
        <div className="text-[10px] text-slate-500 uppercase">{node.state}</div>
      </div>
    </div>
    <div className="flex items-center gap-6">
      <div className="text-right">
        <div className="text-[10px] font-mono text-sky-400">{node.fl} dB</div>
        <div className="text-[9px] text-slate-500 uppercase">FL Eb/No</div>
      </div>
      <div className="text-right w-16">
        <div className="text-[10px] font-bold text-slate-300">{node.traffic}</div>
        <div className="text-[9px] text-slate-500 uppercase">Usage</div>
      </div>
      <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-slate-400 transition-colors" />
    </div>
  </div>
);

const TerminalIA = () => {
  const [lines, setLines] = useState([
    "System: Meru Networks OS v4.0.1 initialized.",
    "Network: Connectivity to Hub stable.",
    "AI: Analyzing March 2026 logs..."
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const messages = [
        "Status: Sun Outage cleared for DC72.",
        "Warning: High latency detected in ZUL36.",
        "Optimization: QoS profiles updated for AMA05.",
        "Report: Monthly availability at 97.8%."
      ];
      setLines(prev => [...prev.slice(-5), `> ${messages[Math.floor(Math.random() * messages.length)]}`]);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black border border-slate-800 rounded-xl overflow-hidden flex flex-col h-full font-mono">
      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Terminal className="w-3 h-3 text-emerald-500" />
          <span className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">NOC_Live_Diagnostics</span>
        </div>
        <div className="flex gap-1.5">
          <div className="w-2 h-2 rounded-full bg-slate-700" />
          <div className="w-2 h-2 rounded-full bg-slate-700" />
        </div>
      </div>
      <div className="p-4 text-[10px] space-y-1.5 text-emerald-500/80 flex-1">
        {lines.map((line, i) => <div key={i} className={i === lines.length - 1 ? "animate-pulse" : ""}>{line}</div>)}
        <div className="text-white">_</div>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <div className="min-h-screen bg-[#020408] text-slate-300 p-4 md:p-8 font-sans selection:bg-sky-500/30">
      
      {/* HEADER INTEGRADO */}
      <header className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 gap-4 border-b border-slate-800 pb-8">
        <div className="flex items-center gap-5">
          <div className="relative">
            <div className="absolute -inset-1 bg-sky-500 rounded-full blur opacity-25 animate-pulse"></div>
            <div className="relative bg-slate-900 p-3 rounded-2xl border border-slate-700">
              <Satellite className="text-sky-400 w-8 h-8" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black tracking-tighter text-white italic">MERU <span className="text-sky-500 not-italic">NETWORKS</span></h1>
              <span className="bg-sky-500/10 text-sky-400 text-[10px] font-black px-2 py-0.5 rounded border border-sky-500/20">VNO-PRO</span>
            </div>
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-[0.2em] mt-1">Satellite Operations & Intelligence Center</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
           <div className="hidden md:flex flex-col text-right mr-4">
              <span className="text-[10px] font-mono text-slate-500">SYSTEM_STATUS</span>
              <span className="text-xs font-bold text-emerald-400">NOMINAL // ALL SYSTEMS GO</span>
           </div>
           <button className="bg-slate-900 border border-slate-700 p-2.5 rounded-xl hover:bg-slate-800 transition-colors">
              <Settings className="w-5 h-5 text-slate-400" />
           </button>
           <button className="bg-sky-500 text-slate-950 px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-sky-400 transition-all shadow-lg shadow-sky-500/20">
              Generate Report
           </button>
        </div>
      </header>

      {/* GRID PRINCIPAL */}
      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LÍNEA DE STATS */}
        <div className="lg:col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Uptime Mensual" value="97.8" unit="%" trend={0.5} icon={ShieldCheck} color="emerald" />
          <StatCard title="Eficiencia Satelital" value="15.1" unit="dB Avg" trend={-1.2} icon={SignalHigh} color="sky" />
          <StatCard title="Tráfico Consumido" value="2.4" unit="TB" trend={8.4} icon={Zap} color="amber" />
          <StatCard title="Tickets Abiertos" value="03" unit="Casos" trend={-20} icon={AlertTriangle} color="rose" />
        </div>

        {/* COLUMNA IZQUIERDA: GRÁFICO Y LISTA */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* PANEL DE GRÁFICO */}
          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl backdrop-blur-sm">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                  <Activity className="w-4 h-4 text-sky-400" /> Rendimiento de Red (Marzo 2026)
                </h3>
                <p className="text-[10px] text-slate-500 mt-1 font-mono">Eb/No Tuner vs Disponibilidad de Enlace</p>
              </div>
              <div className="flex items-center gap-4 bg-black/30 p-2 rounded-lg border border-slate-800">
                <div className="flex items-center gap-2 px-2">
                  <div className="w-2 h-2 rounded-full bg-sky-500" />
                  <span className="text-[10px] font-bold text-slate-400">Eb/No</span>
                </div>
                <div className="flex items-center gap-2 px-2 border-l border-slate-800">
                  <div className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span className="text-[10px] font-bold text-slate-400">Traffic</span>
                </div>
              </div>
            </div>
            
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={PERFORMANCE_DATA}>
                  <defs>
                    <linearGradient id="colorEbNo" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#475569" fontSize={10} tickLine={false} axisLine={false} domain={[12, 16]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                    itemStyle={{ fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="ebno_fl" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorEbNo)" />
                  <Line type="monotone" dataKey="traffic" stroke="#6366f1" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* LISTA DE NODOS */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm">
            <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-800/20">
              <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <Globe className="w-4 h-4 text-emerald-400" /> Status de Remotas Críticas
              </h3>
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500" />
                <input 
                  type="text" 
                  placeholder="Filtrar nodo..." 
                  className="bg-black/40 border border-slate-700 rounded-lg pl-8 pr-4 py-1.5 text-[10px] focus:outline-none focus:border-sky-500 w-48 transition-all"
                />
              </div>
            </div>
            <div className="p-4 space-y-1">
              {NODE_LIST.map(node => <NodeRow key={node.id} node={node} />)}
            </div>
          </div>
        </div>

        {/* COLUMNA DERECHA: IA Y ALERTAS */}
        <div className="lg:col-span-4 space-y-6">
          
          <div className="h-64">
            <TerminalIA />
          </div>

          <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" /> Eventos Pendientes
            </h3>
            <div className="space-y-4">
              <div className="p-3 bg-rose-500/5 border border-rose-500/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-rose-500/20 rounded-lg">
                  <Zap className="w-4 h-4 text-rose-500" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-rose-200">GUA19_HCHF - OFFLINE</div>
                  <p className="text-[10px] text-rose-300/60 mt-1">Falla de energía detectada. Último contacto: 04:10:00. Requiere despacho técnico.</p>
                </div>
              </div>
              
              <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-xl flex gap-3 items-start">
                <div className="p-1.5 bg-amber-500/20 rounded-lg">
                  <SignalHigh className="w-4 h-4 text-amber-500" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-amber-200">ZUL36 - LOW_MARGIN</div>
                  <p className="text-[10px] text-amber-300/60 mt-1">RL Eb/No por debajo del umbral (9.2 dB). Verificar apuntamiento.</p>
                </div>
              </div>

              <div className="p-3 bg-sky-500/5 border border-sky-500/20 rounded-xl flex gap-3 items-start opacity-60">
                <div className="p-1.5 bg-sky-500/20 rounded-lg">
                   <RefreshCw className="w-4 h-4 text-sky-400" />
                </div>
                <div>
                  <div className="text-[11px] font-bold text-sky-200">HUB_CONFIG_SYNC</div>
                  <p className="text-[10px] text-sky-300/60 mt-1">Sincronización de perfiles QoS completada para el segmento VNO.</p>
                </div>
              </div>
            </div>
            
            <button className="w-full mt-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-colors border border-slate-700">
              Ver Historial de Logs
            </button>
          </div>

          <div className="bg-gradient-to-br from-sky-500/20 to-indigo-500/20 border border-sky-500/30 p-6 rounded-2xl relative overflow-hidden group">
            <div className="relative z-10">
              <h4 className="text-white font-bold text-sm">Resumen Ejecutivo Marzo</h4>
              <p className="text-slate-400 text-[10px] mt-2 leading-relaxed">Se superó la meta de disponibilidad en un 0.3%. El Sun Outage del 04-Mar fue mitigado según protocolo.</p>
              <div className="mt-4 flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1,2,3].map(i => (
                    <div key={i} className="w-6 h-6 rounded-full border-2 border-slate-900 bg-slate-800 flex items-center justify-center text-[8px] font-bold">M{i}</div>
                  ))}
                </div>
                <span className="text-[9px] text-slate-500 uppercase font-bold tracking-tighter">Equipo NOC Activo</span>
              </div>
            </div>
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Cpu className="w-16 h-16 text-white" />
            </div>
          </div>
        </div>

      </main>

      <footer className="max-w-7xl mx-auto mt-12 pt-6 border-t border-slate-900 flex justify-between items-center text-[9px] text-slate-600 font-mono uppercase tracking-[0.3em]">
        <div>Meru-Networks // Integrated NOC Environment</div>
        <div>v2.6.0-stable // 2026</div>
      </footer>
    </div>
  );
}
