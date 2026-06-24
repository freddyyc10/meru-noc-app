import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { AlertTriangle, CheckCircle, XCircle, MinusCircle, Clock } from 'lucide-react';
import type { Station } from '@/types/dashboard';

interface SemaforoCriticidadProps {
  stations: Station[];
}

function getStatusIcon(status: Station['status']) {
  switch (status) {
    case 'Operativo':
      return <CheckCircle className="h-3 w-3 text-emerald-500" />;
    case 'Fuera de Servicio':
      return <XCircle className="h-3 w-3 text-red-500" />;
    case 'Intermitente':
      return <AlertTriangle className="h-3 w-3 text-amber-500" />;
    case 'En Espera':
      return <Clock className="h-3 w-3 text-slate-400" />;
    case 'Test':
      return <MinusCircle className="h-3 w-3 text-gray-400" />;
  }
}

function getMarginColor(margin: number): string {
  if (margin >= 5.0) return 'bg-emerald-500';
  if (margin >= 4.0) return 'bg-green-400';
  if (margin >= 3.0) return 'bg-yellow-400';
  if (margin >= 2.0) return 'bg-orange-400';
  if (margin > 0) return 'bg-red-500';
  return 'bg-gray-300';
}

function getMarginLabel(margin: number): string {
  if (margin >= 5.0) return 'Excelente';
  if (margin >= 4.0) return 'Saludable';
  if (margin >= 3.0) return 'Advertencia';
  if (margin >= 2.0) return 'Crítico';
  if (margin > 0) return 'Severo';
  return 'Sin Señal';
}

export function SemaforoCriticidad({ stations }: SemaforoCriticidadProps) {
  const filtered = stations.filter(s => s.id !== 'TEST-01');

  // Sort: offline first, then by margin
  const sorted = [...filtered].sort((a, b) => {
    const statusOrder = { 'Fuera de Servicio': 0, 'Intermitente': 1, 'En Espera': 2, 'Operativo': 3, 'Test': 4 };
    if (statusOrder[a.status] !== statusOrder[b.status]) {
      return statusOrder[a.status] - statusOrder[b.status];
    }
    return a.margin_db - b.margin_db;
  });

  const statusCounts = {
    'Operativo': filtered.filter(s => s.status === 'Operativo').length,
    'Fuera de Servicio': filtered.filter(s => s.status === 'Fuera de Servicio').length,
    'Intermitente': filtered.filter(s => s.status === 'Intermitente').length,
    'En Espera': filtered.filter(s => s.status === 'En Espera').length,
  };

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Semáforo de Criticidad</CardTitle>
          <div className="flex gap-2">
            {Object.entries(statusCounts).map(([status, count]) => (
              <Badge key={status} variant="outline" className="text-xs">
                {status}: {count}
              </Badge>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-2">
            {sorted.map((station) => (
              <Tooltip key={station.id}>
                <TooltipTrigger asChild>
                  <div
                    className={`relative p-2 rounded-lg border cursor-pointer transition-all hover:scale-105 hover:shadow-md ${
                      station.status === 'Fuera de Servicio'
                        ? 'border-red-300 bg-red-50'
                        : station.status === 'Intermitente'
                        ? 'border-amber-300 bg-amber-50'
                        : station.status === 'En Espera'
                        ? 'border-slate-300 bg-slate-50'
                        : 'border-emerald-200 bg-white'
                    }`}
                  >
                    <div className="flex items-center gap-1 mb-1">
                      {getStatusIcon(station.status)}
                      <span className="text-[10px] font-bold truncate">{station.id}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${getMarginColor(station.margin_db)}`} />
                      <span className="text-[9px] text-muted-foreground">
                        {station.margin_db > 0 ? `${station.margin_db}dB` : 'N/A'}
                      </span>
                    </div>
                    <div className={`absolute top-1 right-1 w-1.5 h-1.5 rounded-full ${getMarginColor(station.margin_db)}`} />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-xs">
                  <div className="space-y-1">
                    <p className="font-semibold text-sm">{station.name}</p>
                    <p className="text-xs">Estado: {station.status}</p>
                    <p className="text-xs">Estado: {station.state}</p>
                    <p className="text-xs">Margen: {station.margin_db} dB ({getMarginLabel(station.margin_db)})</p>
                    <p className="text-xs">RL Eb/No: {station.rl_ebno_db} dB</p>
                    <p className="text-xs">FL Eb/No: {station.fl_ebno_db} dB</p>
                    <p className="text-xs text-muted-foreground">{station.maintenance}</p>
                  </div>
                </TooltipContent>
              </Tooltip>
            ))}
          </div>
        </TooltipProvider>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 mt-4 pt-3 border-t text-xs text-muted-foreground">
          <span className="font-medium">Margen de Enlace:</span>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" /> Excelente (≥5dB)</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-400" /> Saludable (4-5dB)</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-yellow-400" /> Advertencia (3-4dB)</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-orange-400" /> Crítico (2-3dB)</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500" /> Severo (&lt;2dB)</div>
          <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-gray-300" /> Sin Señal</div>
        </div>
      </CardContent>
    </Card>
  );
}
