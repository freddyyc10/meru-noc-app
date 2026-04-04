import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { 
  getFirestore, collection, addDoc, onSnapshot, query, 
  doc, updateDoc, deleteDoc, serverTimestamp, getDocs 
} from 'firebase/firestore';
import { 
  Layout, Activity, Database, AlertCircle, FileText, 
  Send, Cpu, RefreshCw, Plus, CheckCircle, Clock, X, ChevronRight, User
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE (PROPORCIONADA POR EL ENTORNO) ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'noc-meru-v2';
const apiKey = ""; // La API Key de Gemini se inyecta automáticamente en tiempo de ejecución

const App = () => {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('dashboard'); // dashboard, history, tickets
  const [analyzing, setAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [newTicket, setNewTicket] = useState({ station: '', issue: '', priority: 'Media' });
  const [isTicketModalOpen, setIsTicketModalOpen] = useState(false);

  // --- AUTENTICACIÓN ---
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Error de Auth:", err);
      }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // --- DATA FETCHING (FIRESTORE) ---
  useEffect(() => {
    if (!user) return;

    // Listener de Archivos/Análisis (Historial)
    const historyCol = collection(db, 'artifacts', appId, 'public', 'data', 'analysis_history');
    const unsubHistory = onSnapshot(historyCol, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setUploadedFiles(data.sort((a, b) => b.timestamp?.seconds - a.timestamp?.seconds));
    }, (err) => console.error("Firestore Error (History):", err));

    // Listener de Tickets
    const ticketsCol = collection(db, 'artifacts', appId, 'public', 'data', 'tickets');
    const unsubTickets = onSnapshot(ticketsCol, (snapshot) => {
      const data = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setTickets(data.sort((a, b) => b.createdAt?.seconds - a.createdAt?.seconds));
    }, (err) => console.error("Firestore Error (Tickets):", err));

    return () => {
      unsubHistory();
      unsubTickets();
    };
  }, [user]);

  // --- INTEGRACIÓN GEMINI 2.5 ---
  const runAiAnalysis = async (content) => {
    setAnalyzing(true);
    setAiAnalysis("");
    
    try {
      const systemPrompt = "Eres un experto en redes satelitales iDirect. Analiza los datos de telemetría proporcionados (Eb/No, Bit Rate, Consumo). Identifica anomalías, degradación de señal por lluvia o fallas de hardware. Responde en español con un formato profesional: 1. Diagnóstico, 2. Recomendación, 3. Nivel de Urgencia.";
      
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `Datos de red para analizar:\n${content}` }] }],
          systemInstruction: { parts: [{ text: systemPrompt }] }
        })
      });

      const data = await response.json();
      const analysisText = data.candidates?.[0]?.content?.parts?.[0]?.text || "No se pudo generar el análisis. Intente nuevamente.";
      setAiAnalysis(analysisText);

      // Guardar en Firestore automáticamente
      if (user) {
        await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'analysis_history'), {
          analysis: analysisText,
          timestamp: serverTimestamp(),
          userName: user.uid,
          fileName: "Reporte_Manual_Análisis.txt"
        });
      }
    } catch (error) {
      setAiAnalysis("Error de conexión con el motor de IA. Verifique su conexión.");
    } finally {
      setAnalyzing(false);
    }
  };

  // --- GESTIÓN DE TICKETS ---
  const handleCreateTicket = async () => {
    if (!newTicket.station || !newTicket.issue) return;
    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'tickets'), {
        ...newTicket,
        status: 'Abierto',
        createdAt: serverTimestamp(),
        createdBy: user.uid
      });
      setNewTicket({ station: '', issue: '', priority: 'Media' });
      setIsTicketModalOpen(false);
    } catch (err) {
      console.error("Error creando ticket:", err);
    }
  };

  const updateTicketStatus = async (id, newStatus) => {
    const docRef = doc(db, 'artifacts', appId, 'public', 'data', 'tickets', id);
    await updateDoc(docRef, { status: newStatus });
  };

  // --- COMPONENTES DE UI ---
  const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${active ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </button>
  );

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 flex flex-col p-6 bg-[#0f172a] z-10">
        <div className="flex items-center gap-3 mb-10">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Activity className="text-white" size={24} />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Meru NOC</h1>
        </div>

        <nav className="flex-1 space-y-2">
          <SidebarItem icon={Layout} label="Dashboard" active={view === 'dashboard'} onClick={() => setView('dashboard')} />
          <SidebarItem icon={Database} label="Historial de Cargas" active={view === 'history'} onClick={() => setView('history')} />
          <SidebarItem icon={AlertCircle} label="Gestor de Tickets" active={view === 'tickets'} onClick={() => setView('tickets')} />
        </nav>

        <div className="mt-auto pt-6 border-t border-slate-800">
          <div className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
              <User size={16} className="text-slate-300" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs text-slate-400">Usuario Activo</p>
              <p className="text-sm font-medium truncate">{user?.uid || 'Anonimo'}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative bg-[#0f172a]">
        <header className="sticky top-0 bg-[#0f172a]/80 backdrop-blur-md border-b border-slate-800 p-6 flex justify-between items-center z-10">
          <div>
            <h2 className="text-2xl font-semibold capitalize">{view}</h2>
            <p className="text-slate-400 text-sm">Monitoreo Inteligente de Red Satelital</p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={() => runAiAnalysis("Estación: Caracas_01, Eb/No: 4.5dB (Bajo), Bitrate: 10Mbps, Status: Intermitente")}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg transition-all font-medium"
            >
              <Cpu size={18} />
              Analizar con Gemini
            </button>
            {view === 'tickets' && (
              <button 
                onClick={() => setIsTicketModalOpen(true)}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-all font-medium"
              >
                <Plus size={18} />
                Nuevo Ticket
              </button>
            )}
          </div>
        </header>

        <div className="p-8">
          {/* Dashboard View */}
          {view === 'dashboard' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Activity className="text-blue-500" /> Estado de la Red
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: 'Estaciones Activas', val: '24', color: 'text-emerald-400' },
                      { label: 'Eb/No Promedio', val: '12.4 dB', color: 'text-blue-400' },
                      { label: 'Tickets Abiertos', val: tickets.filter(t => t.status === 'Abierto').length, color: 'text-amber-400' }
                    ].map((st, i) => (
                      <div key={i} className="bg-slate-800/30 p-4 rounded-xl border border-slate-800/50">
                        <p className="text-slate-400 text-xs mb-1 uppercase tracking-wider">{st.label}</p>
                        <p className={`text-2xl font-bold ${st.color}`}>{st.val}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 min-h-[300px]">
                  <h3 className="text-lg font-semibold mb-4">Análisis Predictivo IA</h3>
                  {analyzing ? (
                    <div className="flex flex-col items-center justify-center h-48 space-y-4">
                      <RefreshCw className="animate-spin text-blue-500" size={32} />
                      <p className="text-slate-400 italic">Gemini está procesando la telemetría...</p>
                    </div>
                  ) : aiAnalysis ? (
                    <div className="bg-indigo-900/20 border border-indigo-500/30 p-5 rounded-xl prose prose-invert max-w-none">
                      <div className="flex items-center gap-2 text-indigo-400 mb-2 font-bold">
                        <Cpu size={16} /> MOTOR GEMINI 2.5 FLASH
                      </div>
                      <div className="whitespace-pre-wrap text-slate-200 text-sm leading-relaxed">
                        {aiAnalysis}
                      </div>
                    </div>
                  ) : (
                    <div className="h-48 flex items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-xl">
                      Haga clic en "Analizar con Gemini" para obtener un diagnóstico técnico.
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-6">
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-semibold mb-4">Últimos Tickets</h3>
                  <div className="space-y-3">
                    {tickets.slice(0, 5).map(ticket => (
                      <div key={ticket.id} className="p-3 bg-slate-800/40 border border-slate-700/50 rounded-lg flex justify-between items-center group hover:bg-slate-800 transition-all">
                        <div>
                          <p className="text-sm font-medium">{ticket.station}</p>
                          <p className="text-xs text-slate-500 truncate w-32">{ticket.issue}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                          ticket.priority === 'Alta' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {ticket.status}
                        </span>
                      </div>
                    ))}
                  </div>
                  <button onClick={() => setView('tickets')} className="w-full mt-4 text-sm text-blue-400 hover:text-blue-300 font-medium">Ver todos los tickets</button>
                </div>
              </div>
            </div>
          )}

          {/* History View */}
          {view === 'history' && (
            <div className="bg-slate-900/40 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/50 border-b border-slate-700">
                    <th className="p-4 font-semibold text-slate-300">Archivo/Reporte</th>
                    <th className="p-4 font-semibold text-slate-300">Fecha de Carga</th>
                    <th className="p-4 font-semibold text-slate-300">Responsable</th>
                    <th className="p-4 font-semibold text-slate-300">Estado de Análisis</th>
                    <th className="p-4 font-semibold text-slate-300 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {uploadedFiles.map((file) => (
                    <tr key={file.id} className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-all">
                      <td className="p-4 flex items-center gap-3">
                        <FileText size={20} className="text-blue-400" />
                        <div>
                          <p className="font-medium">{file.fileName}</p>
                          <p className="text-xs text-slate-500">CSV iDirect NetStats</p>
                        </div>
                      </td>
                      <td className="p-4 text-sm text-slate-400">
                        {file.timestamp?.toDate().toLocaleString() || 'Reciente'}
                      </td>
                      <td className="p-4 text-sm font-mono text-slate-500">
                        {file.userName?.substring(0, 8)}...
                      </td>
                      <td className="p-4">
                        <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full w-fit">
                          <CheckCircle size={12} /> IA Procesado
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <button className="p-2 hover:bg-slate-700 rounded-lg text-slate-400 transition-all">
                          <ChevronRight size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {uploadedFiles.length === 0 && (
                    <tr>
                      <td colSpan="5" className="p-12 text-center text-slate-500 italic">No hay registros de carga en la base de datos.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* Tickets View */}
          {view === 'tickets' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tickets.map(ticket => (
                <div key={ticket.id} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 hover:shadow-xl hover:shadow-blue-900/10 transition-all">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${ticket.priority === 'Alta' ? 'bg-red-500 animate-pulse' : 'bg-amber-500'}`} />
                      <h4 className="font-bold text-lg">{ticket.station}</h4>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      ticket.status === 'Abierto' ? 'bg-blue-600/20 text-blue-400' : 'bg-emerald-600/20 text-emerald-400'
                    }`}>
                      {ticket.status}
                    </span>
                  </div>
                  <p className="text-slate-300 text-sm mb-6 leading-relaxed bg-slate-800/50 p-3 rounded-lg min-h-[80px]">
                    {ticket.issue}
                  </p>
                  <div className="flex justify-between items-center pt-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock size={14} />
                      {ticket.createdAt?.toDate().toLocaleDateString()}
                    </div>
                    <div className="flex gap-2">
                      {ticket.status === 'Abierto' ? (
                        <button 
                          onClick={() => updateTicketStatus(ticket.id, 'Resuelto')}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs rounded transition-colors"
                        >
                          Cerrar Ticket
                        </button>
                      ) : (
                        <button 
                          onClick={() => updateTicketStatus(ticket.id, 'Abierto')}
                          className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white text-xs rounded transition-colors"
                        >
                          Reabrir
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {tickets.length === 0 && (
                <div className="col-span-full py-20 text-center">
                  <div className="bg-slate-800/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <CheckCircle className="text-slate-600" size={32} />
                  </div>
                  <h3 className="text-xl font-medium text-slate-400">Todo en orden</h3>
                  <p className="text-slate-500">No hay fallas reportadas en este momento.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Ticket Modal */}
      {isTicketModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#1e293b] border border-slate-700 w-full max-w-md rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
            <div className="p-6 border-b border-slate-700 flex justify-between items-center">
              <h3 className="text-xl font-bold">Reportar Falla de Red</h3>
              <button onClick={() => setIsTicketModalOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Nombre de la Estación</label>
                <input 
                  type="text" 
                  value={newTicket.station}
                  onChange={(e) => setNewTicket({...newTicket, station: e.target.value})}
                  placeholder="Ej: Caracas_Central_01"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Descripción del Incidente</label>
                <textarea 
                  rows="3"
                  value={newTicket.issue}
                  onChange={(e) => setNewTicket({...newTicket, issue: e.target.value})}
                  placeholder="Describa el problema observado (Latencia, caida de señal, etc.)"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Prioridad</label>
                <select 
                  value={newTicket.priority}
                  onChange={(e) => setNewTicket({...newTicket, priority: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 outline-none"
                >
                  <option>Baja</option>
                  <option>Media</option>
                  <option>Alta</option>
                  <option>Crítica</option>
                </select>
              </div>
            </div>
            <div className="p-6 bg-slate-800/50 flex gap-3">
              <button 
                onClick={() => setIsTicketModalOpen(false)}
                className="flex-1 px-4 py-2 border border-slate-600 rounded-xl hover:bg-slate-700 transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleCreateTicket}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-all shadow-lg shadow-blue-900/20"
              >
                Crear Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
