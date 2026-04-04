import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, collection, addDoc, onSnapshot, query, 
  doc, updateDoc, serverTimestamp 
} from 'firebase/firestore';
import { 
  Activity, Database, AlertCircle, FileText, 
  Cpu, RefreshCw, Plus, CheckCircle, Clock, X, ChevronRight, User, LayoutDashboard, Settings
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'noc-meru-v2';
const apiKey = ""; // La API Key se inyecta automáticamente

const App = () => {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('dashboard'); 
  const [analyzing, setAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [history, setHistory] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ station: '', issue: '', priority: 'Media' });

  // 1. Autenticación Inicial
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Error Auth:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // 2. Carga de Datos en Tiempo Real (Firestore)
  useEffect(() => {
    if (!user) return;

    // Escuchar Historial de Análisis
    const historyCol = collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs');
    const unsubHistory = onSnapshot(historyCol, (snapshot) => {
      setHistory(snapshot.docs.map(d => ({ id: d.id, ...d.data() })));
    }, (err) => console.error("Error Firestore History:", err));

    // Escuchar Tickets de Fallas
    const ticketsCol = collection(db, 'artifacts', appId, 'public', 'data', 'noc_tickets');
    const unsubTickets = onSnapshot(ticketsCol, (snapshot) => {
      setTickets(snapshot.docs.map(d => ({ id: d.id, ...d.data() })));
    }, (err) => console.error("Error Firestore Tickets:", err));

    return () => { unsubHistory(); unsubTickets(); };
  }, [user]);

  // 3. Función de Análisis con Gemini 2.5 Flash
  const analyzeWithGemini = async () => {
    setAnalyzing(true);
    try {
      const mockData = "Estación: San_Cristobal_04. Eb/No: 5.2dB. Status: Degradado. Tráfico: 2Mbps.";
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `Analiza esta telemetría satelital: ${mockData}` }] }],
          systemInstruction: { parts: [{ text: "Eres un experto en redes satelitales. Diagnostica la falla, sugiere solución y asigna prioridad." }] }
        })
      });

      const result = await response.json();
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text || "Error en análisis.";
      setAiAnalysis(text);

      // Guardar log en Base de Datos
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs'), {
        analysis: text,
        station: "San_Cristobal_04",
        timestamp: serverTimestamp(),
        userId: user.uid
      });
    } catch (e) {
      console.error(e);
    } finally {
      setAnalyzing(false);
    }
  };

  // 4. Gestión de Tickets
  const createTicket = async () => {
    if (!newTicket.station || !newTicket.issue) return;
    await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'noc_tickets'), {
      ...newTicket,
      status: 'Abierto',
      createdAt: serverTimestamp(),
      creator: user.uid
    });
    setNewTicket({ station: '', issue: '', priority: 'Media' });
    setIsTicketModalOpen(false);
  };

  const resolveTicket = async (id) => {
    await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', 'noc_tickets', id), {
      status: 'Resuelto'
    });
  };

  return (
    <div className="flex h-screen bg-[#0a0f1d] text-slate-200 font-sans">
      {/* Sidebar de Navegación */}
      <aside className="w-64 border-r border-slate-800 bg-[#0f172a] flex flex-col p-6">
        <div className="flex items-center gap-3 mb-10 text-blue-500">
          <Activity size={28} strokeWidth={2.5} />
          <h1 className="text-xl font-bold tracking-tight text-white">Meru Cloud</h1>
        </div>

        <nav className="flex-1 space-y-2">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Panel Control' },
            { id: 'history', icon: Database, label: 'Logs de Carga' },
            { id: 'tickets', icon: AlertCircle, label: 'Gestor Tickets' }
          ].map(item => (
            <button 
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${view === item.id ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:bg-slate-800'}`}
            >
              <item.icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto p-4 bg-slate-800/40 rounded-2xl flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
            <User size={16} />
          </div>
          <div className="overflow-hidden">
            <p className="text-[10px] text-slate-500 font-bold uppercase">ID Operador</p>
            <p className="text-xs truncate font-mono">{user?.uid || 'Conectando...'}</p>
          </div>
        </div>
      </aside>

      {/* Área Principal */}
      <main className="flex-1 overflow-y-auto">
        <header className="p-8 flex justify-between items-center border-b border-slate-800/50 bg-[#0a0f1d]/50 backdrop-blur">
          <div>
            <h2 className="text-2xl font-bold text-white capitalize">{view.replace('_', ' ')}</h2>
            <p className="text-slate-500 text-sm italic">Infraestructura Satelital Meru Networks</p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={analyzeWithGemini}
              disabled={analyzing}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl transition-all font-bold shadow-lg shadow-indigo-900/20"
            >
              {analyzing ? <RefreshCw className="animate-spin" size={18} /> : <Cpu size={18} />}
              Análisis IA
            </button>
            {view === 'tickets' && (
              <button 
                onClick={() => setIsTicketModalOpen(true)}
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl transition-all font-bold"
              >
                <Plus size={18} /> Nuevo Ticket
              </button>
            )}
          </div>
        </header>

        <div className="p-8">
          {view === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {/* Visualización de IA */}
                <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6 min-h-[300px]">
                  <h3 className="text-lg font-bold mb-4 flex items-center gap-2 text-indigo-400">
                    <Cpu size={20} /> Inteligencia Artificial (Gemini 2.5)
                  </h3>
                  {aiAnalysis ? (
                    <div className="bg-indigo-500/5 border border-indigo-500/20 p-6 rounded-2xl animate-in fade-in duration-500">
                      <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{aiAnalysis}</p>
                    </div>
                  ) : (
                    <div className="h-48 flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800 rounded-2xl">
                      <p>Esperando datos de telemetría para análisis...</p>
                    </div>
                  )}
                </div>

                {/* Status Cards */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800">
                    <p className="text-xs text-slate-500 font-bold mb-1">UPTIME GLOBAL</p>
                    <p className="text-2xl font-bold text-emerald-400">99.82%</p>
                  </div>
                  <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800">
                    <p className="text-xs text-slate-500 font-bold mb-1">STATIONS ONLINE</p>
                    <p className="text-2xl font-bold text-blue-400">42 / 45</p>
                  </div>
                  <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800">
                    <p className="text-xs text-slate-500 font-bold mb-1">PENDIENTES</p>
                    <p className="text-2xl font-bold text-amber-400">{tickets.filter(t => t.status === 'Abierto').length}</p>
                  </div>
                </div>
              </div>

              {/* Sidebar de Tickets Recientes */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-6">
                <h3 className="font-bold mb-4">Tickets Activos</h3>
                <div className="space-y-3">
                  {tickets.filter(t => t.status === 'Abierto').slice(0, 5).map(t => (
                    <div key={t.id} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-2xl hover:border-blue-500/50 transition-colors cursor-pointer group">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-mono text-blue-400">{t.station}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${t.priority === 'Alta' ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-300'}`}>{t.priority}</span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2">{t.issue}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {view === 'history' && (
            <div className="bg-[#111827] border border-slate-800 rounded-3xl overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="p-5 font-bold">Estación</th>
                    <th className="p-5 font-bold">Diagnóstico IA</th>
                    <th className="p-5 font-bold">Operador</th>
                    <th className="p-5 font-bold text-right">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map(log => (
                    <tr key={log.id} className="border-t border-slate-800/50 hover:bg-slate-800/20">
                      <td className="p-5 font-medium">{log.station}</td>
                      <td className="p-5 text-slate-400 italic">"{log.analysis?.substring(0, 60)}..."</td>
                      <td className="p-5 font-mono text-slate-500 text-xs">{log.userId?.substring(0, 8)}</td>
                      <td className="p-5 text-right text-slate-500">{log.timestamp?.toDate().toLocaleString() || 'Sincronizando...'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {view === 'tickets' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tickets.map(t => (
                <div key={t.id} className={`p-6 rounded-3xl border transition-all ${t.status === 'Resuelto' ? 'bg-slate-900/30 border-slate-800 opacity-60' : 'bg-slate-900 border-slate-700 shadow-xl'}`}>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${t.priority === 'Alta' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]' : 'bg-blue-500'}`} />
                      <h4 className="font-bold text-lg text-white">{t.station}</h4>
                    </div>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${t.status === 'Abierto' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-400'}`}>
                      {t.status}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm mb-6 min-h-[60px] leading-relaxed">{t.issue}</p>
                  <div className="flex justify-between items-center pt-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock size={14} />
                      {t.createdAt?.toDate().toLocaleDateString()}
                    </div>
                    {t.status === 'Abierto' && (
                      <button 
                        onClick={() => resolveTicket(t.id)}
                        className="text-xs bg-emerald-600/10 hover:bg-emerald-600 text-emerald-500 hover:text-white px-3 py-1.5 rounded-lg transition-all"
                      >
                        Marcar Resuelto
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modal de Nuevo Ticket */}
      {isTicketModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <div className="bg-[#111827] border border-slate-800 w-full max-w-md rounded-[2.5rem] shadow-2xl animate-in zoom-in duration-200">
            <div className="p-8">
              <h3 className="text-2xl font-bold text-white mb-6">Reportar Incidencia</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Estación Afectada</label>
                  <input 
                    type="text"
                    value={newTicket.station}
                    onChange={(e) => setNewTicket({...newTicket, station: e.target.value})}
                    placeholder="Nombre del Terminal..."
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-2xl p-4 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase mb-2 block">Detalle de Falla</label>
                  <textarea 
                    rows="3"
                    value={newTicket.issue}
                    onChange={(e) => setNewTicket({...newTicket, issue: e.target.value})}
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-2xl p-4 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  />
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={() => setIsTicketModalOpen(false)}
                    className="flex-1 py-4 bg-slate-800 hover:bg-slate-700 rounded-2xl font-bold text-sm transition-all"
                  >
                    Cerrar
                  </button>
                  <button 
                    onClick={createTicket}
                    className="flex-1 py-4 bg-blue-600 hover:bg-blue-500 rounded-2xl font-bold text-sm shadow-lg shadow-blue-900/30 transition-all"
                  >
                    Crear Reporte
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
