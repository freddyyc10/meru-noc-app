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
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import type { Station } from '@/types/dashboard';

interface TrafficChartsProps {
  stations: Station[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

export function TrafficCharts({ stations }: TrafficChartsProps) {
  const filtered = stations.filter(s => s.id !== 'TEST-01' && (s.traffic_in_mb > 0 || s.traffic_out_mb > 0));

  // Sort by total traffic
  const sortedByTraffic = [...filtered].sort((a, b) => 
    (b.traffic_in_mb + b.traffic_out_mb) - (a.traffic_in_mb + a.traffic_out_mb)
  );

  const top20 = sortedByTraffic.slice(0, 20);

  const trafficData = top20.map(s => ({
    station: s.id,
    'Tráfico Entrada': Math.round(s.traffic_in_mb / 1024 * 100) / 100, // Convert to GB
    'Tráfico Salida': Math.round(s.traffic_out_mb / 1024 * 100) / 100,
  }));

  // Pie chart data by state
  const stateTraffic: Record<string, number> = {};
  filtered.forEach(s => {
    if (!stateTraffic[s.state]) stateTraffic[s.state] = 0;
    stateTraffic[s.state] += s.traffic_in_mb + s.traffic_out_mb;
  });

  const pieData = Object.entries(stateTraffic)
    .map(([name, value]) => ({ name, value: Math.round(value / 1024 * 100) / 100 }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-sm">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(2)} GB
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const totalIn = filtered.reduce((sum, s) => sum + s.traffic_in_mb, 0);
  const totalOut = filtered.reduce((sum, s) => sum + s.traffic_out_mb, 0);

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Análisis de Tráfico de Datos</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="bars" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="bars">Top 20 Estaciones</TabsTrigger>
            <TabsTrigger value="states">Por Estado</TabsTrigger>
            <TabsTrigger value="summary">Resumen</TabsTrigger>
          </TabsList>

          <TabsContent value="bars" className="mt-4">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={trafficData} margin={{ top: 5, right: 30, left: 20, bottom: 100 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="station" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  tick={{ fontSize: 9 }}
                />
                <YAxis label={{ value: 'GB', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="Tráfico Entrada" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Tráfico Salida" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>

          <TabsContent value="states" className="mt-4">
            <div className="flex flex-col md:flex-row items-center gap-4">
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={140}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => `${value.toFixed(2)} GB`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="summary" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <p className="text-sm text-muted-foreground">Total Entrada</p>
                <p className="text-2xl font-bold text-blue-600">{(totalIn / 1024).toFixed(1)} GB</p>
              </div>
              <div className="bg-emerald-50 rounded-lg p-4 text-center">
                <p className="text-sm text-muted-foreground">Total Salida</p>
                <p className="text-2xl font-bold text-emerald-600">{(totalOut / 1024).toFixed(1)} GB</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <p className="text-sm text-muted-foreground">Ratio In/Out</p>
                <p className="text-2xl font-bold text-purple-600">
                  {totalOut > 0 ? (totalIn / totalOut).toFixed(2) : 'N/A'}
                </p>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm font-medium mb-2">Top 5 Estaciones por Tráfico:</p>
              <div className="space-y-2">
                {sortedByTraffic.slice(0, 5).map((s, i) => (
                  <div key={s.id} className="flex items-center justify-between bg-gray-50 rounded p-2">
                    <span className="text-sm font-medium">{i + 1}. {s.id}</span>
                    <span className="text-sm text-muted-foreground">
                      {((s.traffic_in_mb + s.traffic_out_mb) / 1024).toFixed(1)} GB
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
