import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { 
  CloudUpload, MessageSquare, Activity, 
  Database, Zap, ChevronRight, Send, Loader2,
  Settings, ShieldCheck, Download, AlertTriangle
} from 'lucide-react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc, onSnapshot, query, doc } from 'firebase/firestore';

// --- CONFIGURACIÓN ---
const apiKey = ""; // Inyectado por el entorno
const appId = typeof __app_id !== 'undefined' ? __app_id : 'meru-networks-hub-v2';

const App = () => {
  const [data, setData] = useState([]);
  const [metrics, setMetrics] = useState({ avg: 0, max: 0, count: 0 });
  const [activeMetric, setActiveMetric] = useState('Seleccione un archivo');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Bienvenido al Hub de Inteligencia de Meru Networks. Cargue un CSV de iDirect para iniciar el análisis de telemetría.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [aiInsight, setAiInsight] = useState('');
  const fileInputRef = useRef(null);

  // --- LÓGICA DE PROCESAMIENTO DE CSV (Reemplaza a Python) ---
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const lines = text.split(/\r?\n/).filter(line => line.trim() !== "");
      
      // 1. Encontrar la cabecera real (ignorando metadatos de iDirect)
      let headerIndex = -1;
      for (let i = 0; i < lines.length; i++) {
        const lowerLine = lines[i].toLowerCase();
        if (lowerLine.includes('time') || lowerLine.includes('date') || lowerLine.includes('eb/no')) {
          headerIndex = i;
          break;
        }
      }

      if (headerIndex === -1) {
        setMessages(prev => [...prev, { role: 'ai', text: '⚠️ Error: No se detectó una estructura válida de iDirect en el CSV.' }]);
        return;
      }

      const headers = lines[headerIndex].split(',').map(h => h.replace(/"/g, '').trim());
      const rows = lines.slice(headerIndex + 1);

      // 2. Identificar columnas clave
      const timeIdx = headers.findIndex(h => /time|date/i.test(h));
      const valIdx = headers.findIndex(h => /eb\/no|rate|traffic|octets|value/i.test(h));

      if (valIdx === -1) {
        setMessages(prev => [...prev, { role: 'ai', text: '⚠️ Error: No se encontró una métrica numérica (Eb/No o Tráfico) en el archivo.' }]);
        return;
      }

      // 3. Mapear datos para el gráfico
      const chartData = rows.map((row, idx) => {
        const cols = row.split(',');
        const val = parseFloat(cols[valIdx]);
        return {
          timestamp: cols[timeIdx] || `T-${idx}`,
          value: isNaN(val) ? 0 : val
        };
      }).filter(d => d.value !== 0);

      if (chartData.length > 0) {
        setData(chartData);
        setActiveMetric(headers[valIdx]);
        const sum = chartData.reduce((a, b) => a + b.value, 0);
        setMetrics({
          avg: (sum / chartData.length).toFixed(2),
          max: Math.max(...chartData.map(d => d.value)).toFixed(2),
          count: chartData.length
        });
        generateAiSummary(chartData, headers[valIdx]);
      }
    };
    reader.readAsText(file);
  };

  // --- INTEGRACIÓN CON GEMINI (Análisis Automático) ---
  const generateAiSummary = async (rawData, metricName) => {
    setIsAnalyzing(true);
    const sample = rawData.slice(0, 15); // Muestra para contexto
    
    const prompt = `Analiza estos datos de telemetría satelital Meru Networks:
    Métrica: ${metricName}
    Muestra: ${JSON.stringify(sample)}
    Proporciona un diagnóstico técnico rápido (máximo 3 líneas) sobre la estabilidad del enlace.`;

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { parts: [{ text: "Eres el experto en NOC de Meru Networks. Sé preciso y técnico." }] }
        })
      });
      const result = await response.json();
      const text = result.candidates[0].content.parts[0].text;
      setAiInsight(text);
      setMessages(prev => [...prev, { role: 'ai', text: 'Análisis de telemetría completado. Revisa el informe en pantalla.' }]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleChat = async () => {
    if (!inputValue.trim()) return;
    const userText = inputValue;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInputValue('');
    setIsAnalyzing(true);

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `Contexto: Métrica ${activeMetric} con promedio ${metrics.avg}. Pregunta: ${userText}` }] }]
        })
      });
      const result = await response.json();
      setMessages(prev => [...prev, { role: 'ai', text: result.candidates[0].content.parts[0].text }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: 'Error en el núcleo de IA.' }]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      {/* Navbar Estilo Meru */}
      <nav className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-[#3f4494] p-1.5 rounded-lg">
              <Activity className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-extrabold tracking-tight flex items-center">
                <span className="text-[#00aeef]">MERU</span>
                <span className="text-[#3f4494] ml-1">NETWORKS</span>
              </h1>
              <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-slate-400">Intelligence Hub v2.0</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <div className="hidden md:block text-right mr-4">
                <p className="text-[10px] font-bold text-slate-400 uppercase">Estado Global</p>
                <p className="text-xs font-bold text-emerald-500">Sistemas Operativos</p>
             </div>
             <button className="bg-slate-100 p-2 rounded-full hover:bg-slate-200 transition-colors">
                <Settings size={20} className="text-slate-600" />
             </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Columna Izquierda: Controles y Chat */}
        <div className="md:col-span-4 space-y-6">
          {/* Carga de Archivos */}
          <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <CloudUpload size={16} /> Importación NMS
            </h3>
            <div 
              onClick={() => fileInputRef.current.click()}
              className="group border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center hover:border-[#00aeef] hover:bg-blue-50/50 transition-all cursor-pointer"
            >
              <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".csv" />
              <div className="w-12 h-12 bg-blue-100 text-[#00aeef] rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                <Database size={24} />
              </div>
              <p className="text-sm font-bold text-slate-700">Subir Reporte iDirect</p>
              <p className="text-[10px] text-slate-400 mt-2 uppercase">CSV de Telemetría (Time, Eb/No...)</p>
            </div>
          </div>

          {/* Chat AI */}
          <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden flex flex-col h-[450px]">
            <div className="bg-[#3f4494] p-4 text-white flex items-center gap-3">
              <Zap size={20} className="text-yellow-400" />
              <span className="font-bold text-sm">Meru AI Assistant</span>
              {isAnalyzing && <Loader2 className="animate-spin ml-auto" size={16} />}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-sm shadow-sm ${
                    m.role === 'user' ? 'bg-[#3f4494] text-white rounded-tr-none' : 'bg-white text-slate-700 border border-slate-100 rounded-tl-none'
                  }`}>
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="p-3 bg-white border-t border-slate-100 flex gap-2">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                placeholder="Consultar sobre la red..."
                className="flex-1 bg-slate-50 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-[#00aeef] transition-all"
              />
              <button onClick={handleChat} className="bg-[#3f4494] text-white p-2 rounded-xl hover:bg-[#2d316e]">
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Columna Derecha: Dashboard */}
        <div className="md:col-span-8 space-y-6">
          {/* Tarjetas de Métricas */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl shadow-sm border-b-4 border-[#3f4494]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Métrica Principal</p>
              <h4 className="text-sm font-bold text-slate-800 truncate mb-2">{activeMetric}</h4>
              <p className="text-2xl font-black text-[#3f4494]">{metrics.avg}</p>
            </div>
            <div className="bg-white p-5 rounded-2xl shadow-sm border-b-4 border-[#00aeef]">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Pico Detectado</p>
              <h4 className="text-sm font-bold text-slate-800 truncate mb-2">Máximo Valor</h4>
              <p className="text-2xl font-black text-[#00aeef]">{metrics.max}</p>
            </div>
            <div className="bg-white p-5 rounded-2xl shadow-sm border-b-4 border-emerald-500">
              <p className="text-[10px] font-bold text-slate-400 uppercase">Muestras</p>
              <h4 className="text-sm font-bold text-slate-800 truncate mb-2">Puntos de Datos</h4>
              <p className="text-2xl font-black text-emerald-600">{metrics.count}</p>
            </div>
          </div>

          {/* Gráfico */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 min-h-[450px]">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h3 className="font-bold text-slate-800 text-lg">Histórico de Telemetría</h3>
                <p className="text-xs text-slate-400 italic">Visualización dinámica de la portadora</p>
              </div>
              <div className="p-1 bg-slate-100 rounded-lg flex gap-1">
                <button className="px-3 py-1 bg-white rounded shadow-sm text-xs font-bold text-[#3f4494]">Tendencia</button>
              </div>
            </div>

            <div className="h-[300px] w-full">
              {data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                    <defs>
                      <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3f4494" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#3f4494" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="timestamp" hide />
                    <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
                    <Area type="monotone" dataKey="value" stroke="#3f4494" strokeWidth={3} fillOpacity={1} fill="url(#colorVal)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-300">
                  <Activity size={48} className="mb-4 opacity-20" />
                  <p className="text-sm font-medium">Esperando datos de entrada...</p>
                </div>
              )}
            </div>
          </div>

          {/* Reporte de IA */}
          {aiInsight && (
            <div className="bg-gradient-to-r from-[#3f4494] to-[#2a2e66] rounded-3xl p-6 text-white shadow-lg animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="bg-white/20 p-2 rounded-lg">
                  <ShieldCheck size={20} />
                </div>
                <h4 className="text-sm font-bold uppercase tracking-widest">Diagnóstico de Inteligencia Meru</h4>
              </div>
              <p className="text-sm leading-relaxed text-blue-50 font-medium">
                {aiInsight}
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
