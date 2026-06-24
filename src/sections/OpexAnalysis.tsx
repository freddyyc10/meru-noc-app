import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { 
  PiggyBank, 
  TrendingDown, 
  Wrench, 
  AlertTriangle,
  Shield,
  Zap,
  CheckCircle
} from 'lucide-react';

const monthlyData = [
  { month: 'Ene', correctivo: 8500, preventivo: 3200 },
  { month: 'Feb', correctivo: 9200, preventivo: 3400 },
  { month: 'Mar', correctivo: 7800, preventivo: 3600 },
  { month: 'Abr', correctivo: 10500, preventivo: 3800 },
  { month: 'May', correctivo: 6800, preventivo: 4000 },
  { month: 'Jun', correctivo: 7200, preventivo: 4200 },
];

const savingsProjection = [
  { month: 'Ene', sin_preventivo: 8500, con_preventivo: 8500 },
  { month: 'Feb', sin_preventivo: 17700, con_preventivo: 11900 },
  { month: 'Mar', sin_preventivo: 25500, con_preventivo: 19100 },
  { month: 'Abr', sin_preventivo: 36000, con_preventivo: 26700 },
  { month: 'May', sin_preventivo: 42800, con_preventivo: 33700 },
  { month: 'Jun', sin_preventivo: 50000, con_preventivo: 40900 },
  { month: 'Jul', sin_preventivo: 58000, con_preventivo: 47000 },
  { month: 'Ago', sin_preventivo: 66000, con_preventivo: 53200 },
  { month: 'Sep', sin_preventivo: 74000, con_preventivo: 59400 },
  { month: 'Oct', sin_preventivo: 82000, con_preventivo: 65600 },
  { month: 'Nov', sin_preventivo: 90000, con_preventivo: 71800 },
  { month: 'Dic', sin_preventivo: 98000, con_preventivo: 78000 },
];

export function OpexAnalysis() {
  const totalCorrectivo = monthlyData.reduce((sum, m) => sum + m.correctivo, 0);
  const totalPreventivo = monthlyData.reduce((sum, m) => sum + m.preventivo, 0);
  const ahorro = totalCorrectivo - totalPreventivo;
  const porcentajeAhorro = (ahorro / totalCorrectivo * 100).toFixed(1);

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <PiggyBank className="h-5 w-5" />
          Análisis de Ahorro OPEX - Preventivo vs Correctivo
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-red-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <span className="text-sm font-medium text-red-700">Costo Correctivo (6 meses)</span>
            </div>
            <p className="text-2xl font-bold text-red-600">${totalCorrectivo.toLocaleString()}</p>
            <p className="text-xs text-red-500 mt-1">Reactivo / Emergencia</p>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="h-4 w-4 text-emerald-500" />
              <span className="text-sm font-medium text-emerald-700">Costo Preventivo (6 meses)</span>
            </div>
            <p className="text-2xl font-bold text-emerald-600">${totalPreventivo.toLocaleString()}</p>
            <p className="text-xs text-emerald-500 mt-1">Planificado / Proactivo</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium text-blue-700">Ahorro Neto</span>
            </div>
            <p className="text-2xl font-bold text-blue-600">${ahorro.toLocaleString()}</p>
            <p className="text-xs text-blue-500 mt-1">{porcentajeAhorro}% de reducción</p>
          </div>
        </div>

        {/* Monthly comparison chart */}
        <div className="mb-6">
          <h4 className="text-sm font-medium mb-3">Comparativa Mensual (USD)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={monthlyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Legend />
              <Bar dataKey="correctivo" name="Correctivo" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="preventivo" name="Preventivo" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cumulative savings projection */}
        <div className="mb-6">
          <h4 className="text-sm font-medium mb-3">Proyección de Ahorro Acumulado Anual (USD)</h4>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={savingsProjection} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="sin_preventivo" 
                name="Sin Preventivo" 
                stroke="#ef4444" 
                fill="#fecaca" 
              />
              <Area 
                type="monotone" 
                dataKey="con_preventivo" 
                name="Con Preventivo" 
                stroke="#10b981" 
                fill="#bbf7d0" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Benefits list */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Beneficios del Preventivo
            </h4>
            <div className="space-y-2">
              {[
                'Reducción del 35.3% en OPEX de soporte',
                'Extensión del 65% en vida útil de transceptores',
                'Menor tasa de fallo de electrónica exterior',
                'Reducción de créditos por penalización SLA',
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-3">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Acciones Preventivas Clave
            </h4>
            <div className="space-y-2">
              {[
                'Alineación mecánica de herrajes',
                'Lubricación de componentes',
                'Re-conectorización hermética',
                'Medición e instalación de barras de tierra',
                'Instalación de reguladores Forza',
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <Shield className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
