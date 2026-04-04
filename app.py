import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, collection, addDoc, onSnapshot, query, 
  doc, updateDoc, serverTimestamp 
} from 'firebase/firestore';
import { 
  Activity, Database, AlertCircle, FileText, 
  Cpu, RefreshCw, Plus, CheckCircle, Clock, 
  ChevronRight, LayoutDashboard, BarChart3, UploadCloud,
  Signal, HardDrive, ShieldAlert
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'noc-meru-app-v2';
const apiKey = ""; // Inyectada por el entorno

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

  // 1. Inicialización de Autenticación
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Auth Error:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // 2. Carga de Datos en Tiempo Real
  useEffect(() => {
    if (!user) return;

    const historyCol = collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs');
    const unsubHistory = onSnapshot(historyCol, (snapshot) => {
      const logs = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
      setHistory(logs.sort((a, b) => (b.timestamp?.seconds || 0) - (a.timestamp?.seconds || 0)));
    }, (err) => console.error("Firestore History Error:", err));

    const ticketsCol = collection(db, 'artifacts', appId, 'public', 'data', 'noc_tickets');
    const unsubTickets = onSnapshot(ticketsCol, (snapshot) => {
      setTickets(snapshot.docs.map(d => ({ id: d.id, ...d.data() })));
    }, (err) => console.error("Firestore Tickets Error:", err));

    return () => { unsubHistory(); unsubTickets(); };
  }, [user]);

  // 3. Procesador de CSV (Lógica de iDirect)
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split('\n');
      // Buscar el inicio de los datos reales (saltando metadatos de iDirect)
      const headerIndex = lines.findIndex(l => 
        l.includes("Date") || l.includes("Time") || l.includes("Eb/No") || l.includes("Octets")
      );
      
      if (headerIndex !== -1) {
        const dataRows = lines.slice(headerIndex, headerIndex + 10); // Tomamos una muestra para el análisis
        setUploadedData({ 
          name: file.name, 
          preview: dataRows.join('\n'),
          fullSize: lines.length 
        });
      }
    };
    reader.readAsText(file);
  };

  // 4. Análisis con Gemini (Sintaxis JavaScript Correcta)
  const analyzeWithGemini = async () => {
    if (!uploadedData) return;
    setAnalyzing(true);
    setAiAnalysis("");
    
    try {
      const prompt = `Analiza este fragmento de reporte NOC satelital (iDirect) e identifica anomalías de Eb/No, saturación de Bit Rate o pérdida de paquetes:\n\n${uploadedData.preview}`;
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { 
            parts: [{ text: "Eres un Ingeniero NOC Senior. Genera un reporte conciso: 1. Estado General, 2. Alertas críticas, 3. Recomendación técnica inmediata." }] 
          }
        })
      });

      const result = await response.json();
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text || "Análisis no disponible.";
      setAiAnalysis(text);

      // Guardar log en Firestore
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'analysis_logs'), {
        analysis: text,
        station: uploadedData.name,
        timestamp: serverTimestamp(),
        userId: user.uid
      });
    } catch (e) {
      console.error("Gemini API Error:", e);
    } finally {
      setAnalyzing(false);
    }
  };

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

  return (
    <div className="flex h-screen bg-[#020617] text-slate-200 font-sans overflow-hidden">
      {/* Sidebar de Navegación */}
      <aside className="w-72 border-r border-slate-800/50 bg-[#070e1e] flex flex-col p-8">
        <div className="flex items-center gap-4 mb-12">
          <div className="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-900/40">
            <Activity size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-black tracking-tighter text-white italic">MERU<span className="text-indigo-400 font-light ml-0.5">NOC</span></h1>
        </div>

        <nav className="flex-1 space-y-2">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: 'Centro de Control' },
            { id: 'history', icon: Database, label: 'Logs de Análisis' },
            { id: 'tickets', icon: ShieldAlert, label: 'Gestión de Fallas' }
          ].map(item => (
            <button 
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all ${view === item.id ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-inner' : 'text-slate-500 hover:bg-slate-800/40 hover:text-slate-300'}`}
            >
              <item.icon size={20} strokeWidth={2} />
              <span className="font-bold text-sm tracking-wide">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto p-5 bg-slate-900/50 border border-slate-800/50 rounded-3xl flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white shadow-md">
            {user?.uid?.charAt(0).toUpperCase() || 'M'}
          </div>
          <div className="overflow-hidden">
            <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-0.5">OP. ID</p>
            <p className="text-xs truncate font-mono text-slate-400">{user?.uid || 'Iniciando...'}</p>
          </div>
        </div>
      </aside>

      {/* Cuerpo Principal */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-gradient-to-b from-[#020617] to-[#070e1e]">
        <header className="p-8 flex justify-between items-center border-b border-slate-800/30 sticky top-0 bg-[#020617]/80 backdrop-blur-xl z-20">
          <div>
            <h2 className="text-3xl font-black text-white tracking-tight">{view === 'dashboard' ? 'Dashboard' : view === 'history' ? 'Logs' : 'Fallas'}</h2>
            <div className="flex items-center gap-2 mt-1">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Sistema Operativo</p>
            </div>
          </div>
          
          <div className="flex gap-4">
            <div className="relative group">
              <input type="file" onChange={handleFileUpload} className="absolute inset-0 opacity-0 cursor-pointer" accept=".csv" />
              <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-2xl transition-all font-bold text-sm border border-slate-700">
                <UploadCloud size={18} /> Cargar Reporte
              </button>
            </div>
            <button 
              onClick={analyzeWithGemini}
              disabled={analyzing || !uploadedData}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-30 text-white px-6 py-3 rounded-2xl transition-all font-bold text-sm shadow-xl shadow-indigo-900/30"
            >
              {analyzing ? <RefreshCw className="animate-spin" size={18} /> : <Cpu size={18} />}
              Diagnóstico IA
            </button>
          </div>
        </header>

        <section className="p-8 flex-1">
          {view === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Bloque Análisis Principal */}
              <div className="lg:col-span-8 space-y-8">
                <div className="bg-slate-900/40 border border-slate-800 rounded-[2.5rem] p-10 relative overflow-hidden">
                  <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-600/10 blur-[100px] rounded-full" />
                  
                  {uploadedData && (
                    <div className="mb-6 flex items-center gap-4 p-4 bg-indigo-600/5 rounded-2xl border border-indigo-500/20">
                      <FileText className="text-indigo-400" />
                      <div>
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Archivo Activo</p>
                        <p className="text-sm font-bold text-white">{uploadedData.name}</p>
                      </div>
                    </div>
                  )}

                  {aiAnalysis ? (
                    <div className="bg-slate-900 border border-slate-800 p-8 rounded-[2rem] animate-in fade-in slide-in-from-bottom-4 duration-500">
                      <div className="flex items-center gap-2 mb-6 text-[10px] font-black text-indigo-400 uppercase tracking-widest">
                        <Cpu size={14} /> Reporte Generado por Gemini v2.5 Flash
                      </div>
                      <div className="prose prose-invert max-w-none prose-p:text-slate-300 prose-p:leading-relaxed text-lg">
                        <p className="whitespace-pre-wrap">{aiAnalysis}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="h-80 flex flex-col items-center justify-center text-slate-700 border-2 border-dashed border-slate-800/50 rounded-[2rem]">
                      <Signal size={64} className="mb-4 opacity-10" />
                      <p className="text-lg font-bold opacity-40">Cargue un CSV para generar diagnóstico</p>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-6">
                  <div className="bg-slate-900/60 p-6 rounded-3xl border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2 tracking-widest">Estaciones</p>
                    <p className="text-4xl font-black text-white">42</p>
                  </div>
                  <div className="bg-slate-900/60 p-6 rounded-3xl border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2 tracking-widest">Tickets Activos</p>
                    <p className="text-4xl font-black text-amber-500">{tickets.filter(t => t.status === 'Abierto').length}</p>
                  </div>
                  <div className="bg-slate-900/60 p-6 rounded-3xl border border-slate-800/50">
                    <p className="text-[10px] text-slate-500 font-black uppercase mb-2 tracking-widest">Diagnósticos</p>
                    <p className="text-4xl font-black text-indigo-400">{history.length}</p>
                  </div>
                </div>
              </div>

              {/* Sidebar Derecha */}
              <div className="lg:col-span-4 space-y-8">
                <div className="bg-slate-900/40 border border-slate-800 rounded-[2.5rem] p-8">
                  <h3 className="font-black text-white mb-6 uppercase tracking-widest text-xs flex items-center gap-2">
                    <Clock size={14} className="text-indigo-400" /> Logs Recientes
                  </h3>
                  <div className="space-y-4">
                    {history.slice(0, 5).map(log => (
                      <div key={log.id} className="p-4 bg-slate-900/80 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer group">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-[10px] font-bold text-indigo-400 truncate w-32">{log.station}</span>
                          <span className="text-[9px] text-slate-600 font-mono">
                            {log.timestamp?.toDate().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 line-clamp-1 italic">"{log.analysis}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {view === 'history' && (
            <div className="bg-slate-900/40 border border-slate-800 rounded-[2.5rem] overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-slate-900/80 border-b border-slate-800">
                  <tr>
                    <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Fuente / Estación</th>
                    <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Resumen IA</th>
                    <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {history.map(log => (
                    <tr key={log.id} className="hover:bg-slate-800/20 transition-colors">
                      <td className="px-8 py-6">
                        <div className="flex items-center gap-3">
                          <FileText size={16} className="text-indigo-400" />
                          <span className="font-bold text-white text-sm">{log.station}</span>
                        </div>
                      </td>
                      <td className="px-8 py-6">
                        <p className="text-slate-400 text-xs line-clamp-2 italic">{log.analysis}</p>
                      </td>
                      <td className="px-8 py-6 text-right">
                        <p className="text-sm font-bold text-slate-300">{log.timestamp?.toDate().toLocaleDateString()}</p>
                        <p className="text-[10px] text-slate-600">{log.timestamp?.toDate().toLocaleTimeString()}</p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {view === 'tickets' && (
            <div className="space-y-8">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-black text-white uppercase tracking-wider">Reportes de Incidencias</h3>
                <button 
                  onClick={() => setIsTicketModalOpen(true)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-2xl font-bold text-sm shadow-xl shadow-indigo-900/40 flex items-center gap-2"
                >
                  <Plus size={18} /> Registrar Falla
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tickets.map(t => (
                  <div key={t.id} className={`p-8 rounded-[2.5rem] border transition-all ${t.status === 'Resuelto' ? 'bg-slate-900/20 border-slate-800/50 opacity-60' : 'bg-slate-900 border-slate-800 shadow-2xl hover:border-indigo-500/30'}`}>
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                           <div className={`w-2 h-2 rounded-full ${t.priority === 'Alta' ? 'bg-red-500 animate-pulse' : 'bg-indigo-500'}`} />
                           <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{t.priority} Prioridad</span>
                        </div>
                        <h4 className="text-xl font-black text-white">{t.station}</h4>
                      </div>
                      <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase ${t.status === 'Abierto' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' : 'bg-slate-800 text-slate-500'}`}>
                        {t.status}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm mb-8 leading-relaxed italic">"{t.issue}"</p>
                    <div className="flex justify-between items-center pt-6 border-t border-slate-800/50">
                      <div className="text-[10px] text-slate-600 font-bold flex items-center gap-1">
                        <Clock size={12} /> {t.createdAt?.toDate().toLocaleDateString()}
                      </div>
                      {t.status === 'Abierto' && (
                        <button 
                          onClick={async () => await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', 'noc_tickets', t.id), { status: 'Resuelto' })}
                          className="text-xs text-emerald-500 font-bold hover:bg-emerald-500/10 px-3 py-1.5 rounded-lg transition-all"
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

      {/* Modal para Nuevo Ticket */}
      {isTicketModalOpen && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center p-6 z-[100]">
          <div className="bg-[#0b1224] border border-slate-800 w-full max-w-xl rounded-[3rem] p-12 shadow-[0_0_80px_rgba(0,0,0,0.5)]">
            <h3 className="text-3xl font-black text-white mb-2">Nueva Incidencia</h3>
            <p className="text-slate-500 mb-10 text-sm">Registre la falla detectada para seguimiento del NOC.</p>
            
            <div className="space-y-6">
              <input 
                type="text"
                value={newTicket.station}
                onChange={(e) => setNewTicket({...newTicket, station: e.target.value})}
                placeholder="Nombre de la Estación"
                className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-5 text-white focus:ring-2 focus:ring-indigo-600 outline-none transition-all"
              />
              <div className="flex gap-2">
                {['Baja', 'Media', 'Alta'].map(p => (
                  <button 
                    key={p}
                    onClick={() => setNewTicket({...newTicket, priority: p})}
                    className={`flex-1 py-3 rounded-xl font-bold text-xs transition-all ${newTicket.priority === p ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-500 border border-slate-800'}`}
                  >
                    {p}
                  </button>
                ))}
              </div>
              <textarea 
                rows="4"
                value={newTicket.issue}
                onChange={(e) => setNewTicket({...newTicket, issue: e.target.value})}
                placeholder="Descripción técnica de la falla..."
                className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-5 text-white focus:ring-2 focus:ring-indigo-600 outline-none transition-all resize-none"
              />
              <div className="flex gap-4 pt-4">
                <button onClick={() => setIsTicketModalOpen(false)} className="flex-1 py-4 bg-slate-800 text-white rounded-2xl font-bold">Cancelar</button>
                <button onClick={createTicket} className="flex-1 py-4 bg-indigo-600 text-white rounded-2xl font-bold shadow-lg shadow-indigo-900/30">Abrir Ticket</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
