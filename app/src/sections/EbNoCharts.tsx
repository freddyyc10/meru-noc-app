import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import type { Station } from '@/types/dashboard';

interface EbNoChartsProps {
  stations: Station[];
}

interface ChartDataPoint {
  station: string;
  rl_ebno: number;
  fl_ebno: number;
  margin: number;
  status: string;
}

export function EbNoCharts({ stations }: EbNoChartsProps) {
  const filtered = stations.filter(s => s.id !== 'TEST-01');

  // Sort by margin ascending to show critical first
  const sortedByMargin = [...filtered].sort((a, b) => a.margin_db - b.margin_db);

  const chartData: ChartDataPoint[] = sortedByMargin.map(s => ({
    station: s.id,
    rl_ebno: s.rl_ebno_db,
    fl_ebno: s.fl_ebno_db,
    margin: s.margin_db,
    status: s.status,
  }));

  // Group by status for distribution
  const statusGroups = {
    'Saludable (≥4dB)': filtered.filter(s => s.margin_db >= 4.0).length,
    'Riesgo (2-4dB)': filtered.filter(s => s.margin_db >= 2.0 && s.margin_db < 4.0).length,
    'Crítico (<2dB)': filtered.filter(s => s.margin_db > 0 && s.margin_db < 2.0).length,
    'Sin Señal': filtered.filter(s => s.margin_db === 0).length,
  };

  const distributionData = Object.entries(statusGroups).map(([name, value]) => ({
    name,
    value,
    fill: name.includes('Saludable') ? '#10b981' : 
         name.includes('Riesgo') ? '#f59e0b' : 
         name.includes('Crítico') ? '#f97316' : '#9ca3af',
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-sm">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(2)} dB
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Análisis de Eb/No y Margen de Enlace</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="margin" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="margin">Margen por Estación</TabsTrigger>
            <TabsTrigger value="ebno">RL vs FL Eb/No</TabsTrigger>
            <TabsTrigger value="dist">Distribución</TabsTrigger>
          </TabsList>

          <TabsContent value="margin" className="mt-4">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="station" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  tick={{ fontSize: 9 }}
                />
                <YAxis label={{ value: 'dB', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar 
                  dataKey="margin" 
                  name="Margen de Enlace" 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
            <div className="text-center text-xs text-muted-foreground mt-2">
              Ordenado por margen (menor a mayor)
            </div>
          </TabsContent>

          <TabsContent value="ebno" className="mt-4">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData.slice(0, 30)} margin={{ top: 5, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="station" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  tick={{ fontSize: 9 }}
                />
                <YAxis label={{ value: 'dB', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="rl_ebno" name="RL Eb/No" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="fl_ebno" name="FL Eb/No" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="text-center text-xs text-muted-foreground mt-2">
              Primeras 30 estaciones - Ordenadas por criticidad
            </div>
          </TabsContent>

          <TabsContent value="dist" className="mt-4">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={distributionData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" name="Estaciones" radius={[0, 4, 4, 0]}>
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
