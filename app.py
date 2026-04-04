import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, collection, addDoc, onSnapshot, query, 
  doc, updateDoc, serverTimestamp 
} from 'firebase/firestore';
import { 
  Activity, Database, AlertCircle, FileText, 
  Cpu, RefreshCw, Plus, CheckCircle, Clock, X, 
  ChevronRight, User, LayoutDashboard, BarChart3, UploadCloud
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'noc-meru-suite';
const apiKey = ""; // Inyectada automáticamente por el entorno

const App = () => {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('dashboard'); 
  const [analyzing, setAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [history, setHistory] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);
  const [uploadedData, setUploadedData] = useState(null);
  const [newTicket, setNewTicket] = useState({ station: '', issue: '', priority: 'Media' });

  // 1. Autenticación Robusta (Regla 3)
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

  // 2. Escucha de Datos en Tiempo Real (Firestore - Regla 1 y 2)
  useEffect(() => {
    if (!user) return;

    const historyCol = collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs');
    const unsubHistory = onSnapshot(historyCol, (snapshot) => {
      const logs = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
      setHistory(logs.sort((a, b) => (b.timestamp?.seconds || 0) - (a.timestamp?.seconds || 0)));
    }, (err) => console.error("Error History:", err));

    const ticketsCol = collection(db, 'artifacts', appId, 'public', 'data', 'noc_tickets');
    const unsubTickets = onSnapshot(ticketsCol, (snapshot) => {
      setTickets(snapshot.docs.map(d => ({ id: d.id, ...d.data() })));
    }, (err) => console.error("Error Tickets:", err));

    return () => { unsubHistory(); unsubTickets(); };
  }, [user]);

  // 3. Procesador de CSV (Lógica migrada de app.py)
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n');
      // Lógica de limpieza: buscar cabecera
      const headerIndex = lines.findIndex(l => l.includes("Date") || l.includes("Time") || l.includes("Eb/No"));
      if (headerIndex !== -1) {
        const data = lines.slice(headerIndex).map(l => l.split(','));
        setUploadedData({ name: file.name, preview: data.slice(1, 5) });
      }
    };
    reader.readAsText(file);
  };

  // 4. Análisis con Gemini 2.5 Flash (Sintaxis Corregida)
  const analyzeWithGemini = async () => {
    if (!uploadedData) return;
    setAnalyzing(true);
    try {
      const context = `Archivo: ${uploadedData.name}. Datos: ${JSON.stringify(uploadedData.preview)}`;
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `Analiza este reporte NOC satelital y detecta anomalías: ${context}` }] }],
          systemInstruction: { parts: [{ text: "Eres un experto en NOC. Resume fallas en 3 puntos clave, asigna severidad y recomienda acciones técnicas." }] }
        })
      });

      const result = await response.json();
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text || "No se pudo generar el análisis.";
      setAiAnalysis(text);

      // Guardar en Firestore (Regla 1)
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs'), {
        analysis: text,
        station: uploadedData.name,
        timestamp: serverTimestamp(),
        userId: user.uid
      });
    } catch (e) {
      console.error("Gemini Error:", e);
    } finally {
      setAnalyzing(false);
    }
  };

  // 5. Gestión de Tickets
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
    <div className="flex h-screen bg-[#020617] text-slate-200 font-sans overflow-hidden">
      {/* Sidebar Navegación */}
      <aside className="w-72 border-r border-slate-800 bg-[#070e1e] flex flex-col p-8">
        <div className="flex items-center gap-4 mb-12">
          <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-900/40">
            <Activity size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-black tracking-tight text-white italic">MERU<span className="text-blue-500 font-normal ml-1">NOC</span></h1>
        </div>

        <nav className="flex-1 space-y-3">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Panel Principal' },
            { id: 'history', icon: Database, label: 'Logs de IA' },
            { id: 'tickets', icon: AlertCircle, label: 'Fallas / Tickets' }
          ].map(item => (
            <button 
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-300 ${view === item.id ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20' : 'text-slate-500 hover:bg-slate-800/40 hover:text-slate-300'}`}
            >
              <item.icon size={20} strokeWidth={view === item.id ? 2.5 : 2} />
              <span className="font-semibold text-sm">{item.label}</span>
              {view === item.id && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />}
            </button>
          ))}
        </nav>

        <div className="mt-auto p-5 bg-slate-900/50 border border-slate-800/50 rounded-3xl flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg">
            {user?.uid?.substring(0,1).toUpperCase() || 'M'}
          </div>
          <div className="overflow-hidden">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-0.5">Operador Activo</p>
            <p className="text-xs truncate font-mono text-slate-300">{user?.uid || 'Conectando...'}</p>
          </div>
        </div>
      </aside>

      {/* Área de Contenido */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="p-10 flex justify-between items-center bg-[#020617]/80 backdrop-blur-md sticky top-0 z-10 border-b border-slate-800/30">
          <div>
            <h2 className="text-3xl font-black text-white tracking-tight capitalize">{view.replace('_', ' ')}</h2>
            <p className="text-slate-500 text-sm mt-1">Supervisión Inteligente de Enlaces Satelitales</p>
          </div>
          <div className="flex gap-4">
            <div className="relative group">
              <input 
                type="file" 
                onChange={handleFileUpload} 
                className="absolute inset-0 opacity-0 cursor-pointer" 
                accept=".csv"
              />
              <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-2xl transition-all font-bold text-sm">
                <UploadCloud size={18} /> Cargar CSV
              </button>
            </div>
            <button 
              onClick={analyzeWithGemini}
              disabled={analyzing || !uploadedData}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white px-6 py-3 rounded-2xl transition-all font-bold text-sm shadow-xl shadow-indigo-900/30"
            >
              {analyzing ? <RefreshCw className="animate-spin" size={18} /> : <Cpu size={18} />}
              Diagnosticar IA
            </button>
          </div>
        </header>

        <section className="flex-1 overflow-y-auto p-10">
          {view === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Bloque de Análisis IA */}
              <div className="lg:col-span-8 space-y-8">
                <div className="bg-[#0b1224] border border-slate-800 rounded-[2.5rem] p-8 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600/5 blur-[100px] rounded-full" />
                  <h3 className="text-xl font-bold mb-6 flex items-center gap-3 text-indigo-400">
                    <div className="p-2 bg-indigo-500/10 rounded-lg"><Cpu size={22} /></div>
                    Análisis en Tiempo Real
                  </h3>
                  
                  {aiAnalysis ? (
                    <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-[2rem] animate-in fade-in slide-in-from-bottom-4 duration-700">
                      <div className="flex items-center gap-2 mb-4 text-xs font-bold text-slate-500">
                        <FileText size={14} /> REPORTE GENERADO POR GEMINI 2.5 FLASH
                      </div>
                      <p className="text-slate-300 leading-relaxed text-lg whitespace-pre-wrap">{aiAnalysis}</p>
                    </div>
                  ) : (
                    <div className="h-64 flex flex-col items-center justify-center text-slate-600 border-2 border-dashed border-slate-800 rounded-[2rem] bg-slate-900/20">
                      <BarChart3 size={48} className="mb-4 opacity-20" />
                      <p className="text-lg font-medium">Sube un reporte CSV para iniciar el diagnóstico</p>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-slate-900/40 p-6 rounded-[2rem] border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2">Uptime Satelital</p>
                    <p className="text-3xl font-black text-emerald-400">99.98%</p>
                  </div>
                  <div className="bg-slate-900/40 p-6 rounded-[2rem] border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2">Tickets Abiertos</p>
                    <p className="text-3xl font-black text-blue-400">{tickets.filter(t => t.status === 'Abierto').length}</p>
                  </div>
                  <div className="bg-slate-900/40 p-6 rounded-[2rem] border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2">Logs de IA</p>
                    <p className="text-3xl font-black text-indigo-400">{history.length}</p>
                  </div>
                </div>
              </div>

              {/* Sidebar de Actividad */}
              <div className="lg:col-span-4">
                <div className="bg-[#0b1224]/50 border border-slate-800/50 rounded-[2.5rem] p-8 h-full">
                  <div className="flex justify-between items-center mb-8">
                    <h3 className="font-black text-white text-lg">Reportes Recientes</h3>
                    <button onClick={() => setView('history')} className="text-xs text-blue-500 font-bold hover:underline">Ver Todo</button>
                  </div>
                  <div className="space-y-4">
                    {history.slice(0, 6).map(h => (
                      <div key={h.id} className="p-4 bg-slate-900/80 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer group">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-[10px] font-bold text-indigo-400 truncate max-w-[120px]">{h.station}</span>
                          <span className="text-[9px] text-slate-600">{h.timestamp?.toDate().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                        <p className="text-xs text-slate-500 line-clamp-1 italic">"{h.analysis}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {view === 'history' && (
            <div className="bg-[#0b1224] border border-slate-800 rounded-[2.5rem] overflow-hidden shadow-2xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-slate-900/80 border-b border-slate-800">
                    <tr>
                      <th className="px-8 py-6 text-xs font-black text-slate-500 uppercase tracking-widest">Archivo / Estación</th>
                      <th className="px-8 py-6 text-xs font-black text-slate-500 uppercase tracking-widest">Diagnóstico Gemini</th>
                      <th className="px-8 py-6 text-xs font-black text-slate-500 uppercase tracking-widest text-right">Fecha / Hora</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {history.map(log => (
                      <tr key={log.id} className="hover:bg-slate-800/20 transition-colors group">
                        <td className="px-8 py-6">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-slate-800 rounded-lg text-slate-400 group-hover:text-blue-400 transition-colors"><FileText size={16} /></div>
                            <span className="font-bold text-white text-sm">{log.station}</span>
                          </div>
                        </td>
                        <td className="px-8 py-6">
                          <p className="text-slate-400 text-sm leading-relaxed max-w-2xl line-clamp-2 italic">"{log.analysis}"</p>
                        </td>
                        <td className="px-8 py-6 text-right">
                          <p className="text-sm font-medium text-slate-300">{log.timestamp?.toDate().toLocaleDateString()}</p>
                          <p className="text-[10px] text-slate-600 font-bold">{log.timestamp?.toDate().toLocaleTimeString()}</p>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {view === 'tickets' && (
            <div className="space-y-8">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-bold text-white">Tickets de Operación</h3>
                <button 
                  onClick={() => setIsTicketModalOpen(true)}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-2xl font-bold text-sm transition-all flex items-center gap-2"
                >
                  <Plus size={18} /> Nuevo Reporte
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {tickets.map(t => (
                  <div key={t.id} className={`p-8 rounded-[2.5rem] border transition-all ${t.status === 'Resuelto' ? 'bg-slate-900/20 border-slate-800 opacity-50' : 'bg-slate-900 border-slate-700 shadow-2xl hover:border-blue-500/50'}`}>
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${t.priority === 'Alta' ? 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.6)]' : 'bg-blue-500'}`} />
                        <h4 className="font-black text-xl text-white">{t.station}</h4>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter ${t.status === 'Abierto' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-500'}`}>
                        {t.status}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm mb-8 leading-relaxed min-h-[60px]">{t.issue}</p>
                    <div className="flex justify-between items-center pt-6 border-t border-slate-800">
                      <div className="flex items-center gap-2 text-[10px] text-slate-600 font-bold">
                        <Clock size={12} />
                        {t.createdAt?.toDate().toLocaleDateString()}
                      </div>
                      {t.status === 'Abierto' && (
                        <button 
                          onClick={() => resolveTicket(t.id)}
                          className="text-xs bg-emerald-500/10 hover:bg-emerald-500 text-emerald-500 hover:text-white px-4 py-2 rounded-xl transition-all font-bold"
                        >
                          Cerrar Ticket
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Modal de Tickets */}
      {isTicketModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center p-6 z-50 animate-in fade-in duration-300">
          <div className="bg-[#0b1224] border border-slate-800 w-full max-w-xl rounded-[3rem] shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
            <div className="p-12">
              <h3 className="text-3xl font-black text-white mb-2">Reportar Incidencia</h3>
              <p className="text-slate-500 mb-10 text-sm">Crea un ticket para el seguimiento de fallas en sitio.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 block">Identificador de Estación</label>
                  <input 
                    type="text"
                    value={newTicket.station}
                    onChange={(e) => setNewTicket({...newTicket, station: e.target.value})}
                    placeholder="Ej: San_Cristobal_02"
                    className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-5 text-white focus:ring-2 focus:ring-blue-600 outline-none transition-all placeholder:text-slate-700 font-medium"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 block">Prioridad de Atención</label>
                  <div className="flex gap-3">
                    {['Baja', 'Media', 'Alta'].map(p => (
                      <button 
                        key={p}
                        onClick={() => setNewTicket({...newTicket, priority: p})}
                        className={`flex-1 py-3 rounded-xl font-bold text-xs transition-all ${newTicket.priority === p ? 'bg-blue-600 text-white shadow-lg' : 'bg-slate-900 text-slate-500 border border-slate-800'}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 block">Descripción Técnica</label>
                  <textarea 
                    rows="4"
                    value={newTicket.issue}
                    onChange={(e) => setNewTicket({...newTicket, issue: e.target.value})}
                    placeholder="Describe los síntomas observados..."
                    className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-5 text-white focus:ring-2 focus:ring-blue-600 outline-none transition-all placeholder:text-slate-700 font-medium resize-none"
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button 
                    onClick={() => setIsTicketModalOpen(false)}
                    className="flex-1 py-5 bg-slate-800 hover:bg-slate-700 text-white rounded-2xl font-bold text-sm transition-all"
                  >
                    Cancelar
                  </button>
                  <button 
                    onClick={createTicket}
                    className="flex-1 py-5 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-bold text-sm shadow-xl shadow-blue-900/40 transition-all"
                  >
                    Abrir Ticket
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
