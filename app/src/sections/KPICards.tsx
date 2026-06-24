import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Satellite, 
  AlertTriangle, 
  TrendingDown, 
  Wifi,
  ArrowDownToLine,
  ArrowUpFromLine,
  PiggyBank,
  Gauge
} from 'lucide-react';
import type { KPIs } from '@/types/dashboard';

interface KPICardsProps {
  kpis: KPIs;
}

export function KPICards({ kpis }: KPICardsProps) {
  const cards = [
    {
      title: 'Disponibilidad de Red',
      value: `${kpis.availability_percent}%`,
      description: 'SLA Promedio',
      icon: Wifi,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-50',
    },
    {
      title: 'Estaciones Operativas',
      value: `${kpis.operational}`,
      description: `de ${kpis.total_stations} totales`,
      icon: Satellite,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Fuera de Servicio',
      value: `${kpis.out_of_service}`,
      description: 'Requieren intervención',
      icon: AlertTriangle,
      color: 'text-red-500',
      bgColor: 'bg-red-50',
    },
    {
      title: 'Intermitentes',
      value: `${kpis.intermittent}`,
      description: 'Nodos degradados',
      icon: TrendingDown,
      color: 'text-amber-500',
      bgColor: 'bg-amber-50',
    },
    {
      title: 'Margen Promedio',
      value: `${kpis.avg_margin_db} dB`,
      description: kpis.avg_margin_db >= 4 ? 'Saludable' : 'En Riesgo',
      icon: Gauge,
      color: kpis.avg_margin_db >= 4 ? 'text-emerald-500' : 'text-red-500',
      bgColor: kpis.avg_margin_db >= 4 ? 'bg-emerald-50' : 'bg-red-50',
    },
    {
      title: 'Tráfico Total Entrada',
      value: `${(kpis.total_traffic_in_mb / 1024).toFixed(1)} GB`,
      description: 'Acumulado período',
      icon: ArrowDownToLine,
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-50',
    },
    {
      title: 'Tráfico Total Salida',
      value: `${(kpis.total_traffic_out_mb / 1024).toFixed(1)} GB`,
      description: 'Acumulado período',
      icon: ArrowUpFromLine,
      color: 'text-indigo-500',
      bgColor: 'bg-indigo-50',
    },
    {
      title: 'Ahorro OPEX',
      value: `${kpis.opex_savings_percent}%`,
      description: 'vs Correctivo',
      icon: PiggyBank,
      color: 'text-green-500',
      bgColor: 'bg-green-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <Card key={index} className="border shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${card.bgColor}`}>
                <Icon className={`h-4 w-4 ${card.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{card.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
