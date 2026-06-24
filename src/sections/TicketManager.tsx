import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Ticket, 
  Plus, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  User, 
  Calendar,
  Wrench,
  Search
} from 'lucide-react';
import type { Ticket as TicketType } from '@/types/dashboard';

const INITIAL_TICKETS: TicketType[] = [
  {
    id: 'TK-771122',
    station: 'AMA06_PAVONI',
    issue: 'Falla ODU - Sin señal de retorno',
    priority: 'Alta',
    status: 'Pendiente',
    assigned_to: 'Miguel Mora',
    created_date: '2026-06-15',
    cost: '$1,000.00',
  },
  {
    id: 'TK-771123',
    station: 'APU13_CUNAVICHE',
    issue: 'Falla energía comercial - 10 días sin servicio',
    priority: 'Alta',
    status: 'Pendiente',
    assigned_to: 'Freddy Yaguaramay',
    created_date: '2026-06-18',
    cost: '$900.00',
  },
  {
    id: 'SAT-001',
    station: 'BAR27_NUTRIAS',
    issue: 'Falla energía eléctrica - Pueblo sin Corpoelec',
    priority: 'Alta',
    status: 'Pendiente',
    assigned_to: 'Sin asignar',
    created_date: '2026-06-20',
    cost: '$950.00',
  },
  {
    id: 'TK-771124',
    station: 'BAR15_ALTAMIRA',
    issue: 'Desapuntamiento post-lluvias - Reapuntamiento requerido',
    priority: 'Media',
    status: 'Resuelto',
    assigned_to: 'Miguel Mora',
    created_date: '2026-07-25',
    resolved_date: '2026-07-29',
    cost: '$950.00',
  },
  {
    id: 'TK-771125',
    station: 'FAL01_LAPENA',
    issue: 'Cortocircuito BUC 3W - Sobretensión Corpoelec',
    priority: 'Alta',
    status: 'Resuelto',
    assigned_to: 'Richard Moreno',
    created_date: '2026-06-10',
    resolved_date: '2026-06-12',
    cost: '$900.00',
  },
  {
    id: 'TK-771126',
    station: 'DC72_WARAIRAREPANO',
    issue: 'Obstrucción Fresnel - Reubicación mástil requerida',
    priority: 'Media',
    status: 'Resuelto',
    assigned_to: 'Miguel Mora',
    created_date: '2026-05-20',
    resolved_date: '2026-05-22',
    cost: '$600.00',
  },
  {
    id: 'TK-771127',
    station: 'ARA12_LAS_TASAJERAS',
    issue: 'Espera logística - Repuestos en tránsito',
    priority: 'Media',
    status: 'Diagnosis',
    assigned_to: 'Soporte NOC',
    created_date: '2026-06-05',
    cost: '$600.00',
  },
  {
    id: 'TK-771128',
    station: 'FAL_URUMACO',
    issue: 'Obra civil pendiente - Loza de concreto',
    priority: 'Baja',
    status: 'Pendiente',
    assigned_to: 'Cliente / Ingeniería Civil',
    created_date: '2026-04-01',
    cost: '$850.00',
  },
];

export function TicketManager() {
  const [tickets, setTickets] = useState<TicketType[]>(INITIAL_TICKETS);
  const [showNewForm, setShowNewForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [newTicket, setNewTicket] = useState<Partial<TicketType>>({
    priority: 'Media',
    status: 'Pendiente',
  });

  const filteredTickets = tickets.filter(t => 
    t.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.station.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.issue.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: TicketType['status']) => {
    switch (status) {
      case 'Pendiente':
        return <Badge variant="destructive"><Clock className="h-3 w-3 mr-1" /> Pendiente</Badge>;
      case 'Diagnosis':
        return <Badge className="bg-blue-500"><Wrench className="h-3 w-3 mr-1" /> Diagnosis</Badge>;
      case 'Resuelto':
        return <Badge className="bg-emerald-500"><CheckCircle2 className="h-3 w-3 mr-1" /> Resuelto</Badge>;
    }
  };

  const getPriorityBadge = (priority: TicketType['priority']) => {
    switch (priority) {
      case 'Alta':
        return <Badge variant="outline" className="text-red-600 border-red-300"><AlertTriangle className="h-3 w-3 mr-1" /> Alta</Badge>;
      case 'Media':
        return <Badge variant="outline" className="text-amber-600 border-amber-300">Media</Badge>;
      case 'Baja':
        return <Badge variant="outline" className="text-blue-600 border-blue-300">Baja</Badge>;
    }
  };

  const handleAddTicket = () => {
    if (newTicket.station && newTicket.issue) {
      const ticket: TicketType = {
        id: `TK-${771129 + tickets.length}`,
        station: newTicket.station,
        issue: newTicket.issue,
        priority: newTicket.priority as TicketType['priority'],
        status: 'Pendiente',
        assigned_to: newTicket.assigned_to || 'Sin asignar',
        created_date: new Date().toISOString().split('T')[0],
        cost: newTicket.cost || '$0.00',
      };
      setTickets([ticket, ...tickets]);
      setShowNewForm(false);
      setNewTicket({ priority: 'Media', status: 'Pendiente' });
    }
  };

  const handleStatusChange = (ticketId: string, newStatus: TicketType['status']) => {
    setTickets(tickets.map(t => 
      t.id === ticketId 
        ? { ...t, status: newStatus, resolved_date: newStatus === 'Resuelto' ? new Date().toISOString().split('T')[0] : t.resolved_date }
        : t
    ));
  };

  const statusCounts = {
    all: filteredTickets.length,
    pending: filteredTickets.filter(t => t.status === 'Pendiente').length,
    diagnosis: filteredTickets.filter(t => t.status === 'Diagnosis').length,
    resolved: filteredTickets.filter(t => t.status === 'Resuelto').length,
  };

  const renderTicketList = (ticketList: TicketType[]) => (
    <div className="space-y-3">
      {ticketList.map(ticket => (
        <div 
          key={ticket.id} 
          className={`border rounded-lg p-4 transition-all hover:shadow-md ${
            ticket.status === 'Resuelto' ? 'bg-emerald-50 border-emerald-200' : 
            ticket.status === 'Diagnosis' ? 'bg-blue-50 border-blue-200' :
            ticket.priority === 'Alta' ? 'bg-red-50 border-red-200' : 'bg-white'
          }`}
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-mono font-semibold">{ticket.id}</span>
                {getStatusBadge(ticket.status)}
                {getPriorityBadge(ticket.priority)}
              </div>
              <p className="text-sm font-medium">{ticket.station}</p>
              <p className="text-xs text-muted-foreground">{ticket.issue}</p>
            </div>
            <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {ticket.assigned_to}
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {ticket.created_date}
              </div>
              {ticket.cost && <span className="font-medium">{ticket.cost}</span>}
            </div>
          </div>
          {ticket.status !== 'Resuelto' && (
            <div className="mt-3 flex gap-2">
              {ticket.status === 'Pendiente' && (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="text-xs"
                  onClick={() => handleStatusChange(ticket.id, 'Diagnosis')}
                >
                  <Wrench className="h-3 w-3 mr-1" />
                  Iniciar Diagnosis
                </Button>
              )}
              <Button 
                size="sm" 
                variant="outline" 
                className="text-xs text-emerald-600"
                onClick={() => handleStatusChange(ticket.id, 'Resuelto')}
              >
                <CheckCircle2 className="h-3 w-3 mr-1" />
                Marcar Resuelto
              </Button>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <Card className="border shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Ticket className="h-5 w-5" />
            NMS Helpdesk - Gestión de Tickets
          </CardTitle>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar ticket..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 w-40"
              />
            </div>
            <Button size="sm" onClick={() => setShowNewForm(!showNewForm)}>
              <Plus className="h-4 w-4 mr-1" />
              Nuevo
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {showNewForm && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
            <h4 className="text-sm font-medium mb-3">Nuevo Ticket</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Input
                placeholder="Estación VSAT"
                value={newTicket.station || ''}
                onChange={e => setNewTicket({ ...newTicket, station: e.target.value })}
              />
              <Select 
                value={newTicket.priority} 
                onValueChange={(v) => setNewTicket({ ...newTicket, priority: v as TicketType['priority'] })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Prioridad" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Alta">Alta</SelectItem>
                  <SelectItem value="Media">Media</SelectItem>
                  <SelectItem value="Baja">Baja</SelectItem>
                </SelectContent>
              </Select>
              <Textarea
                placeholder="Descripción del problema"
                value={newTicket.issue || ''}
                onChange={e => setNewTicket({ ...newTicket, issue: e.target.value })}
                className="md:col-span-2"
              />
              <Input
                placeholder="Asignado a"
                value={newTicket.assigned_to || ''}
                onChange={e => setNewTicket({ ...newTicket, assigned_to: e.target.value })}
              />
              <Input
                placeholder="Costo estimado ($)"
                value={newTicket.cost || ''}
                onChange={e => setNewTicket({ ...newTicket, cost: e.target.value })}
              />
            </div>
            <div className="flex justify-end gap-2 mt-3">
              <Button size="sm" variant="outline" onClick={() => setShowNewForm(false)}>Cancelar</Button>
              <Button size="sm" onClick={handleAddTicket}>Crear Ticket</Button>
            </div>
          </div>
        )}

        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">Todos ({statusCounts.all})</TabsTrigger>
            <TabsTrigger value="pending">Pendientes ({statusCounts.pending})</TabsTrigger>
            <TabsTrigger value="diagnosis">Diagnosis ({statusCounts.diagnosis})</TabsTrigger>
            <TabsTrigger value="resolved">Resueltos ({statusCounts.resolved})</TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-4">
            {renderTicketList(filteredTickets)}
          </TabsContent>
          <TabsContent value="pending" className="mt-4">
            {renderTicketList(filteredTickets.filter(t => t.status === 'Pendiente'))}
          </TabsContent>
          <TabsContent value="diagnosis" className="mt-4">
            {renderTicketList(filteredTickets.filter(t => t.status === 'Diagnosis'))}
          </TabsContent>
          <TabsContent value="resolved" className="mt-4">
            {renderTicketList(filteredTickets.filter(t => t.status === 'Resuelto'))}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
