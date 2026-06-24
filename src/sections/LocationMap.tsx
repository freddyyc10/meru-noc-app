import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { MapPin } from 'lucide-react';
import type { Station } from '@/types/dashboard';

interface LocationMapProps {
  stations: Station[];
}

// State coordinates for Venezuela (approximate center points)
const stateCoordinates: Record<string, { x: number; y: number }> = {
  'Amazonas': { x: 35, y: 75 },
  'Apure': { x: 30, y: 55 },
  'Aragua': { x: 52, y: 38 },
  'Barinas': { x: 28, y: 48 },
  'Carabobo': { x: 48, y: 35 },
  'Delta Amacuro': { x: 75, y: 45 },
  'Distrito Capital': { x: 54, y: 36 },
  'Falcón': { x: 38, y: 22 },
  'Guárico': { x: 55, y: 50 },
  'La Guaira': { x: 56, y: 34 },
  'Mérida': { x: 20, y: 42 },
  'Miranda': { x: 58, y: 38 },
  'Portuguesa': { x: 38, y: 42 },
  'Sucre': { x: 65, y: 35 },
  'Táchira': { x: 15, y: 48 },
  'Trujillo': { x: 32, y: 32 },
  'Yaracuy': { x: 45, y: 33 },
  'Zulia': { x: 18, y: 25 },
};

function getStatusIcon(status: Station['status']) {
  switch (status) {
    case 'Operativo':
      return <div className="w-3 h-3 rounded-full bg-emerald-500" />;
    case 'Fuera de Servicio':
      return <div className="w-3 h-3 rounded-full bg-red-500" />;
    case 'Intermitente':
      return <div className="w-3 h-3 rounded-full bg-amber-500" />;
    case 'En Espera':
      return <div className="w-3 h-3 rounded-full bg-slate-400" />;
    case 'Test':
      return <div className="w-3 h-3 rounded-full bg-gray-300" />;
  }
}

export function LocationMap({ stations }: LocationMapProps) {
  const filtered = stations.filter(s => s.id !== 'TEST-01');
  
  // Group stations by state
  const stateGroups: Record<string, Station[]> = {};
  filtered.forEach(s => {
    if (!stateGroups[s.state]) stateGroups[s.state] = [];
    stateGroups[s.state].push(s);
  });

  // Calculate state status (worst status wins)
  const stateStatus: Record<string, { status: Station['status']; count: number }> = {};
  Object.entries(stateGroups).forEach(([state, stns]) => {
    const hasOffline = stns.some(s => s.status === 'Fuera de Servicio');
    const hasIntermittent = stns.some(s => s.status === 'Intermitente');
    const hasOnHold = stns.some(s => s.status === 'En Espera');
    
    let status: Station['status'] = 'Operativo';
    if (hasOffline) status = 'Fuera de Servicio';
    else if (hasIntermittent) status = 'Intermitente';
    else if (hasOnHold) status = 'En Espera';
    
    stateStatus[state] = { status, count: stns.length };
  });

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <MapPin className="h-5 w-5" />
          Mapa de Ubicaciones - Red Satelital Meru
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Simplified SVG Map of Venezuela */}
        <div className="relative w-full aspect-[4/3] bg-blue-50 rounded-lg border overflow-hidden">
          <svg viewBox="0 0 100 80" className="w-full h-full">
            {/* Venezuela outline - simplified */}
            <path
              d="M10,20 Q15,15 25,18 L35,16 Q40,12 48,15 L55,12 Q60,10 65,14 L72,12 Q78,14 80,20 L82,28 Q85,35 82,42 L85,48 Q88,55 82,60 L78,65 Q72,70 65,68 L58,72 Q50,75 42,70 L35,68 Q28,70 22,65 L18,58 Q12,55 14,48 L12,42 Q8,35 12,28 Z"
              fill="#dbeafe"
              stroke="#3b82f6"
              strokeWidth="0.5"
            />
            {/* Caribbean Sea label */}
            <text x="70" y="18" fontSize="3" fill="#3b82f6" opacity="0.5">Mar Caribe</text>
            {/* Colombia label */}
            <text x="12" y="35" fontSize="2.5" fill="#6b7280" opacity="0.5">Colombia</text>
            {/* Brazil label */}
            <text x="80" y="55" fontSize="2.5" fill="#6b7280" opacity="0.5">Brasil</text>
          </svg>

          {/* Station markers */}
          <TooltipProvider>
            {Object.entries(stateGroups).map(([state, stns]) => {
              const coords = stateCoordinates[state];
              if (!coords) return null;
              
              const status = stateStatus[state];
              const offsetX = coords.x;
              const offsetY = coords.y;

              return (
                <Tooltip key={state}>
                  <TooltipTrigger asChild>
                    <div
                      className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                      style={{ left: `${offsetX}%`, top: `${offsetY}%` }}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 border-white shadow-md flex items-center justify-center ${
                        status.status === 'Fuera de Servicio' ? 'bg-red-500' :
                        status.status === 'Intermitente' ? 'bg-amber-500' :
                        status.status === 'En Espera' ? 'bg-slate-400' :
                        'bg-emerald-500'
                      }`}>
                        <span className="text-[8px] text-white font-bold">{status.count}</span>
                      </div>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    <div className="space-y-1">
                      <p className="font-semibold text-sm">{state}</p>
                      <p className="text-xs">{stns.length} estación(es)</p>
                      {stns.map(s => (
                        <div key={s.id} className="flex items-center gap-1 text-xs">
                          {getStatusIcon(s.status)}
                          <span>{s.id}</span>
                          <span className="text-muted-foreground">({s.margin_db}dB)</span>
                        </div>
                      ))}
                    </div>
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </TooltipProvider>
        </div>

        {/* State summary */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
          {Object.entries(stateGroups)
            .sort((a, b) => b[1].length - a[1].length)
            .map(([state, stns]) => {
              const offline = stns.filter(s => s.status === 'Fuera de Servicio').length;
              const intermittent = stns.filter(s => s.status === 'Intermitente').length;
              return (
                <div key={state} className="flex items-center gap-2 p-2 bg-gray-50 rounded text-xs">
                  <MapPin className="h-3 w-3 text-blue-500" />
                  <div>
                    <span className="font-medium">{state}</span>
                    <span className="text-muted-foreground ml-1">({stns.length})</span>
                    {offline > 0 && <span className="text-red-500 ml-1">{offline} off</span>}
                    {intermittent > 0 && <span className="text-amber-500 ml-1">{intermittent} int</span>}
                  </div>
                </div>
              );
            })}
        </div>
      </CardContent>
    </Card>
  );
}
