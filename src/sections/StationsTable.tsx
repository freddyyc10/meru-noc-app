import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Search, Filter, ChevronDown, ArrowUpDown, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';
import type { Station } from '@/types/dashboard';

interface StationsTableProps {
  stations: Station[];
}

type SortField = 'id' | 'state' | 'status' | 'margin_db' | 'rl_ebno_db' | 'fl_ebno_db' | 'traffic_in_mb' | 'traffic_out_mb';
type SortDirection = 'asc' | 'desc';

export function StationsTable({ stations }: StationsTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [stateFilter, setStateFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('margin_db');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const filtered = stations.filter(s => {
    const matchesSearch = s.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         s.state.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         s.maintenance.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || s.status === statusFilter;
    const matchesState = stateFilter === 'all' || s.state === stateFilter;
    return matchesSearch && matchesStatus && matchesState;
  });

  const sorted = [...filtered].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return sortDirection === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const uniqueStates = [...new Set(stations.map(s => s.state))].sort();

  const getStatusBadge = (status: Station['status']) => {
    switch (status) {
      case 'Operativo':
        return <Badge className="bg-emerald-500 hover:bg-emerald-600"><CheckCircle className="h-3 w-3 mr-1" /> Operativo</Badge>;
      case 'Fuera de Servicio':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" /> Fuera de Servicio</Badge>;
      case 'Intermitente':
        return <Badge className="bg-amber-500 hover:bg-amber-600"><AlertTriangle className="h-3 w-3 mr-1" /> Intermitente</Badge>;
      case 'En Espera':
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" /> En Espera</Badge>;
      case 'Test':
        return <Badge variant="outline">Test</Badge>;
    }
  };

  const getMarginColor = (margin: number) => {
    if (margin >= 5.0) return 'text-emerald-600 font-semibold';
    if (margin >= 4.0) return 'text-green-600';
    if (margin >= 3.0) return 'text-yellow-600';
    if (margin >= 2.0) return 'text-orange-600';
    if (margin > 0) return 'text-red-600 font-semibold';
    return 'text-gray-400';
  };

  const SortIcon = ({ field }: { field: SortField }) => (
    <ArrowUpDown className={`h-3 w-3 ml-1 inline ${sortField === field ? 'text-blue-500' : 'text-gray-300'}`} />
  );

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <CardTitle className="text-lg font-semibold">Detalle de Estaciones VSAT</CardTitle>
          <div className="flex flex-wrap gap-2">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar estación..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 w-48"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-1" />
                  Estado
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setStatusFilter('all')}>Todos</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('Operativo')}>Operativo</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('Fuera de Servicio')}>Fuera de Servicio</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('Intermitente')}>Intermitente</DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter('En Espera')}>En Espera</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-1" />
                  {stateFilter === 'all' ? 'Estado' : stateFilter}
                  <ChevronDown className="h-3 w-3 ml-1" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setStateFilter('all')}>Todos</DropdownMenuItem>
                {uniqueStates.map(state => (
                  <DropdownMenuItem key={state} onClick={() => setStateFilter(state)}>{state}</DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        <div className="text-xs text-muted-foreground mt-1">
          Mostrando {sorted.length} de {stations.length} estaciones
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="cursor-pointer" onClick={() => toggleSort('id')}>
                  ID <SortIcon field="id" />
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => toggleSort('state')}>
                  Ubicación <SortIcon field="state" />
                </TableHead>
                <TableHead className="cursor-pointer" onClick={() => toggleSort('status')}>
                  Estado <SortIcon field="status" />
                </TableHead>
                <TableHead className="cursor-pointer text-right" onClick={() => toggleSort('margin_db')}>
                  Margen (dB) <SortIcon field="margin_db" />
                </TableHead>
                <TableHead className="cursor-pointer text-right" onClick={() => toggleSort('rl_ebno_db')}>
                  RL Eb/No <SortIcon field="rl_ebno_db" />
                </TableHead>
                <TableHead className="cursor-pointer text-right" onClick={() => toggleSort('fl_ebno_db')}>
                  FL Eb/No <SortIcon field="fl_ebno_db" />
                </TableHead>
                <TableHead className="cursor-pointer text-right" onClick={() => toggleSort('traffic_in_mb')}>
                  Traffic In <SortIcon field="traffic_in_mb" />
                </TableHead>
                <TableHead className="cursor-pointer text-right" onClick={() => toggleSort('traffic_out_mb')}>
                  Traffic Out <SortIcon field="traffic_out_mb" />
                </TableHead>
                <TableHead>Último Mantenimiento</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sorted.map((station) => (
                <TableRow key={station.id} className={station.status === 'Fuera de Servicio' ? 'bg-red-50' : station.status === 'Intermitente' ? 'bg-amber-50' : ''}>
                  <TableCell className="font-medium text-xs">{station.id}</TableCell>
                  <TableCell className="text-xs">{station.state}</TableCell>
                  <TableCell>{getStatusBadge(station.status)}</TableCell>
                  <TableCell className={`text-right text-xs ${getMarginColor(station.margin_db)}`}>
                    {station.margin_db > 0 ? `${station.margin_db} dB` : 'N/A'}
                  </TableCell>
                  <TableCell className="text-right text-xs">{station.rl_ebno_db > 0 ? `${station.rl_ebno_db} dB` : 'N/A'}</TableCell>
                  <TableCell className="text-right text-xs">{station.fl_ebno_db > 0 ? `${station.fl_ebno_db} dB` : 'N/A'}</TableCell>
                  <TableCell className="text-right text-xs">{(station.traffic_in_mb / 1024).toFixed(2)} GB</TableCell>
                  <TableCell className="text-right text-xs">{(station.traffic_out_mb / 1024).toFixed(2)} GB</TableCell>
                  <TableCell className="text-xs max-w-[150px] truncate" title={station.maintenance}>
                    {station.maintenance}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
