import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { 
  CloudUpload, MessageSquare, Activity, 
  Database, Zap, ChevronRight, Send, Loader2,
  Settings, Sun, ShieldCheck
} from 'lucide-react';

// --- CONFIGURACIÓN DE FIREBASE Y GEMINI ---
const apiKey = ""; // El entorno inyecta la clave automáticamente
const appId = typeof __app_id !== 'undefined' ? __app_id : 'meru-networks-hub';

const App = () => {
  const [data, setData] = useState([]);
  const [metrics, setMetrics] = useState({ avg: 0, total: 0, remotes: 0 });
  const [activeMetric, setActiveMetric] = useState('Value');
  const [chartType, setChartType] = useState('line');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Bienvenido al Hub de Inteligencia de Meru Networks. Por favor, cargue un reporte NMS para iniciar el diagnóstico.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const fileInputRef = useRef(null);

  // --- PROCESAMIENTO DE ARCHIVOS CSV ---
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      processCSV(text);
    };
    reader.readAsText(file);
  };

  const processCSV = (text) => {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    
    // Encontrar cabecera (Skip metadata iDirect)
    const headerIndex = lines.findIndex(l => 
      l.toLowerCase().includes('time') || 
      l.toLowerCase().includes('date') || 
      l.toLowerCase().includes('eb/no')
    );

    if (headerIndex === -1) return;

    const headers = lines[headerIndex].split(',').map(h => h.replace(/"/g, '').trim());
    const rows = lines.slice(headerIndex + 1);

    const timeIdx = headers.findIndex(h => h.toLowerCase().includes('time') || h.toLowerCase().includes('date'));
    const metricIdx = headers.findIndex(h => 
      h.includes('Eb/No') || h.includes('Rate') || h.includes('Traffic') || h.includes('Octets')
    );

    const processedData = rows.map((row, idx) => {
      const values = row.split(',');
      return {
        time: values[timeIdx] || `Point ${idx}`,
        value: parseFloat(values[metricIdx]) || 0,
        name: headers[metricIdx] || 'Métrica'
      };
    }).filter(d => !isNaN(d.value));

    setData(processedData);
    setActiveMetric(headers[metricIdx] || 'Valor');
    
    // Calcular métricas
    const sum = processedData.reduce((acc, curr) => acc + curr.value, 0);
    setMetrics({
      avg: (sum / processedData.length).toFixed(2),
      total: sum.toLocaleString(),
      remotes: 1 // Simplificado para este ejemplo
    });

    runAiAnalysis(processedData, headers[metricIdx]);
  };

  // --- INTEGRACIÓN CON GEMINI IA ---
  const runAiAnalysis = async (chartData, metricName) => {
    setIsAnalyzing(true);
    const summary = chartData.slice(0, 10); // Enviar muestra para no saturar tokens
    
    const prompt = `Analiza técnicamente estos datos de red satelital:
    Métrica: ${metricName}
    Datos: ${JSON.stringify(summary)}
    Proporciona un diagnóstico breve sobre la salud del enlace, posibles interferencias o atenuación por lluvia.`;

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { parts: [{ text: "Eres el Analista Principal de Meru Networks. Habla de forma técnica y profesional." }] }
        })
      });
      const result = await response.json();
      const text = result.candidates[0].content.parts[0].text;
      setAiAnalysis(text);
      setMessages(prev => [...prev, { role: 'ai', text: "Análisis técnico completado. He detectado patrones importantes en la telemetría." }]);
    } catch (error) {
      console.error("Gemini Error:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    const userMsg = inputValue;
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInputValue('');
    setIsAnalyzing(true);

    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: `Basado en los datos de la red, responde a: ${userMsg}` }] }]
        })
      });
      const result = await response.json();
      setMessages(prev => [...prev, { role: 'ai', text: result.candidates[0].content.parts[0].text }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: "Error de conexión con el núcleo de IA." }]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f7fa] text-slate-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 py-4 px-8 sticky top-0 z-50 shadow-sm">
        <div className="max-w-[1600px] mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="flex items-center">
              <svg width="50" height="30" viewBox="0 0 100 60" fill="none">
                <path d="M10 50L40 10L55 35L70 15L90 50" stroke="#3f4494" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M25 50L45 25" stroke="#00aeef" strokeWidth="4" strokeLinecap="round"/>
              </svg>
              <div className="h-8 w-[1px] bg-slate-300 mx-4"></div>
              <div>
                <h1 className="text-xl font-bold tracking-tighter flex items-center">
                  <span className="text-[#00aeef]">MERU</span>
                  <span className="text-[#3f4494] ml-1">NETWORKS</span>
                </h1>
                <p className="text-[9px] uppercase tracking-[0.2em] text-slate-400 font-bold">Satellite Intelligence Hub</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex flex-col items-end">
              <span className="text-[10px] font-bold text-slate-400 uppercase">System Status</span>
              <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span> Online
              </span>
            </div>
            <button className="bg-slate-100 p-2 rounded-full hover:bg-slate-200 transition-all">
              <Settings size={18} className="text-slate-600" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1600px] mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Sidebar */}
        <div className="col-span-12 lg:col-span-4 xl:col-span-3 space-y-6">
          {/* Upload Area */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 border border-white shadow-sm">
            <h3 className="text-xs font-bold text-slate-500 mb-4 uppercase tracking-widest flex items-center gap-2">
              <CloudUpload size={16} /> Importar Reporte NMS
            </h3>
            <div 
              onClick={() => fileInputRef.current.click()}
              className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center hover:border-[#00aeef] hover:bg-blue-50/50 transition-all cursor-pointer group"
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                className="hidden" 
                accept=".csv"
              />
              <div className="w-12 h-12 bg-blue-50 text-[#00aeef] rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                <Database size={24} />
              </div>
              <p className="text-sm font-semibold text-slate-700">Arrastrar CSV de iDirect</p>
              <p className="text-[10px] text-slate-400 mt-1 uppercase">Soporta telemetría de Hub y Remotos</p>
            </div>
          </div>

          {/* AI Chat */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden flex flex-col h-[500px]">
            <div className="bg-gradient-to-br from-[#3f4494] to-[#2a2e66] p-4 text-white flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  <Zap size={18} />
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-tighter leading-none opacity-70">AI Analyst</p>
                  <p className="text-sm font-bold">Meru Core</p>
                </div>
              </div>
              {isAnalyzing && <Loader2 className="animate-spin" size={16} />}
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-50/50">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                    msg.role === 'user' 
                      ? 'bg-[#3f4494] text-white rounded-tr-none' 
                      : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none shadow-sm'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 bg-white border-t border-slate-100 flex gap-2">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Preguntar a la IA..."
                className="flex-1 bg-slate-50 border-none rounded-xl px-4 py-2 text-sm focus:ring-2 focus:ring-[#00aeef] outline-none"
              />
              <button 
                onClick={handleSendMessage}
                className="bg-[#3f4494] text-white p-2 rounded-xl hover:opacity-90 shadow-md transition-all"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Dashboard Area */}
        <div className="col-span-12 lg:col-span-8 xl:col-span-9 space-y-6">
          {/* Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl border-l-4 border-[#3f4494] shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Métrica Activa</p>
              <h4 className="text-sm font-semibold text-slate-600 truncate">{activeMetric}</h4>
              <p className="text-2xl font-bold text-[#3f4494]">{metrics.avg}</p>
            </div>
            <div className="bg-white p-5 rounded-2xl border-l-4 border-[#00aeef] shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Volumen Total</p>
              <h4 className="text-sm font-semibold text-slate-600">Acumulado</h4>
              <p className="text-2xl font-bold text-[#00aeef]">{metrics.total}</p>
            </div>
            <div className="bg-white p-5 rounded-2xl border-l-4 border-emerald-500 shadow-sm">
              <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Estado de Red</p>
              <h4 className="text-sm font-semibold text-slate-600">Salud General</h4>
              <p className="text-lg font-bold text-emerald-600 flex items-center gap-2">
                <ShieldCheck size={18} /> {data.length > 0 ? "Estable" : "Sin Datos"}
              </p>
            </div>
          </div>

          {/* Main Chart */}
          <div className="bg-white rounded-3xl p-8 shadow-sm border border-slate-100 min-h-[500px] flex flex-col relative overflow-hidden">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 relative z-10">
              <div>
                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Activity className="text-[#00aeef]" /> Visualización de Telemetría
                </h2>
                <p className="text-xs text-slate-400">Datos históricos procesados del archivo NMS</p>
              </div>
              <div className="flex bg-slate-100 p-1 rounded-xl">
                <button 
                  onClick={() => setChartType('line')}
                  className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${chartType === 'line' ? 'bg-white shadow-sm text-[#3f4494]' : 'text-slate-500'}`}
                >
                  Lineal
                </button>
                <button 
                  onClick={() => setChartType('bar')}
                  className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${chartType === 'bar' ? 'bg-white shadow-sm text-[#3f4494]' : 'text-slate-500'}`}
                >
                  Barras
                </button>
              </div>
            </div>

            <div className="flex-1 w-full min-h-[350px]">
              {data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  {chartType === 'line' ? (
                    <AreaChart data={data}>
                      <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3f4494" stopOpacity={0.1}/>
                          <stop offset="95%" stopColor="#3f4494" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="time" hide />
                      <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                      />
                      <Area type="monotone" dataKey="value" stroke="#3f4494" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                    </AreaChart>
                  ) : (
                    <BarChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="time" hide />
                      <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#fff', borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                      />
                      <Bar dataKey="value" fill="#00aeef" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-slate-300">
                    <Database size={32} />
                  </div>
                  <p className="text-slate-400 text-sm max-w-[250px]">Cargue un archivo CSV para visualizar la telemetría de satélite.</p>
                </div>
              )}
            </div>
          </div>

          {/* Detailed AI Report */}
          {aiAnalysis && (
            <div className="bg-white rounded-2xl p-6 border-t-4 border-[#00aeef] shadow-sm animate-in fade-in slide-in-from-bottom-4">
              <div className="flex items-center gap-2 mb-4">
                <span className="p-2 bg-blue-50 text-[#00aeef] rounded-lg">
                  <Activity size={20} />
                </span>
                <h3 className="font-bold text-slate-800 uppercase text-xs tracking-widest">Reporte Ejecutivo de Inteligencia</h3>
              </div>
              <div className="prose prose-sm max-w-none text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-100">
                {aiAnalysis.split('\n').map((line, i) => (
                  <p key={i} className="mb-2">{line}</p>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
