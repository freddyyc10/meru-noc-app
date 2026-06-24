export interface Station {
  id: string;
  name: string;
  state: string;
  status: 'Operativo' | 'Fuera de Servicio' | 'Intermitente' | 'En Espera' | 'Test';
  maintenance: string;
  cost: string;
  distance: string;
  margin_db: number;
  rl_ebno_db: number;
  fl_ebno_db: number;
  traffic_in_mb: number;
  traffic_out_mb: number;
  band: string;
}

export interface KPIs {
  total_stations: number;
  operational: number;
  out_of_service: number;
  intermittent: number;
  on_hold: number;
  availability_percent: number;
  avg_margin_db: number;
  total_traffic_in_mb: number;
  total_traffic_out_mb: number;
  critical_stations: number;
  healthy_stations: number;
  opex_savings_percent: number;
  date_range: {
    start: string;
    end: string;
  };
}

export interface DashboardData {
  stations: Station[];
  kpis: KPIs;
  historical: Record<string, any>;
}

export interface Ticket {
  id: string;
  station: string;
  issue: string;
  priority: 'Alta' | 'Media' | 'Baja';
  status: 'Pendiente' | 'Diagnosis' | 'Resuelto';
  assigned_to: string;
  created_date: string;
  resolved_date?: string;
  cost?: string;
}
