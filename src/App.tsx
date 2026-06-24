import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Satellite, 
  LayoutDashboard, 
  Activity, 
  TrafficCone, 
  Table2, 
  Ticket, 
  MapPin, 
  PiggyBank,
  RefreshCw,
  Wifi,
  Upload,
  Menu,
  X,
  AlertTriangle
} from 'lucide-react';
import { useDashboardData } from '@/hooks/useDashboardData';
import { KPICards } from '@/sections/KPICards';
import { SemaforoCriticidad } from '@/sections/SemaforoCriticidad';
import { EbNoCharts } from '@/sections/EbNoCharts';
import { TrafficCharts } from '@/sections/TrafficCharts';
import { StationsTable } from '@/sections/StationsTable';
import { TicketManager } from '@/sections/TicketManager';
import { LocationMap } from '@/sections/LocationMap';
import { OpexAnalysis } from '@/sections/OpexAnalysis';
import { FileUploader } from '@/sections/FileUploader';
import './App.css';

function App() {
  const { data, loading, error, fileName, processExcelFile } = useDashboardData();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    if (data) {
      setLastUpdate(new Date());
    }
  }, [data]);

  if (loading && !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 text-blue-500 animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Cargando DAS Meru Networks...</h2>
          <p className="text-sm text-gray-500 mt-2">Inicializando dashboard satelital</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700">Error cargando datos</h2>
          <p className="text-sm text-gray-500 mt-2">{error || 'No se pudieron cargar los datos del dashboard'}</p>
        </div>
      </div>
    );
  }

  const { stations, kpis } = data;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <Button 
                variant="ghost" 
                size="icon" 
                className="md:hidden"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              <div className="flex items-center gap-2">
                <div className="bg-blue-600 p-2 rounded-lg">
                  <Satellite className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-900 leading-tight">DAS Meru Networks</h1>
                  <p className="text-[10px] text-gray-500 leading-tight">Red Satelital VSAT Ku-Band</p>
                </div>
              </div>
            </div>

            {/* Center - Quick Stats */}
            <div className="hidden lg:flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 rounded-full">
                <Wifi className="h-4 w-4 text-emerald-500" />
                <span className="text-sm font-medium text-emerald-700">{kpis.availability_percent}% Disponibilidad</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1 bg-blue-50 rounded-full">
                <Satellite className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-blue-700">{kpis.operational}/{kpis.total_stations} Operativas</span>
              </div>
              {kpis.out_of_service > 0 && (
                <div className="flex items-center gap-2 px-3 py-1 bg-red-50 rounded-full">
                  <Activity className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-medium text-red-700">{kpis.out_of_service} Fuera de Servicio</span>
                </div>
              )}
            </div>

            {/* Right - Update info */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:block text-right">
                <p className="text-xs text-muted-foreground">Última actualización</p>
                <p className="text-xs font-medium">{lastUpdate.toLocaleString()}</p>
              </div>
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                <RefreshCw className="h-3 w-3 mr-1" />
                NOC-Sync
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1600px] mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Tab Navigation */}
          <div className="mb-6 overflow-x-auto">
            <TabsList className="inline-flex h-10 items-center justify-start rounded-md bg-muted p-1 text-muted-foreground w-auto min-w-full">
              <TabsTrigger value="dashboard" className="inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm">
                <LayoutDashboard className="h-4 w-4 mr-1" />
                Dashboard
              </TabsTrigger>
              <TabsTrigger value="ebno">
                <Activity className="h-4 w-4 mr-1" />
                Eb/No
              </TabsTrigger>
              <TabsTrigger value="traffic">
                <TrafficCone className="h-4 w-4 mr-1" />
                Tráfico
              </TabsTrigger>
              <TabsTrigger value="stations">
                <Table2 className="h-4 w-4 mr-1" />
                Estaciones
              </TabsTrigger>
              <TabsTrigger value="tickets">
                <Ticket className="h-4 w-4 mr-1" />
                Tickets
              </TabsTrigger>
              <TabsTrigger value="map">
                <MapPin className="h-4 w-4 mr-1" />
                Mapa
              </TabsTrigger>
              <TabsTrigger value="opex">
                <PiggyBank className="h-4 w-4 mr-1" />
                OPEX
              </TabsTrigger>
              <TabsTrigger value="upload">
                <Upload className="h-4 w-4 mr-1" />
                Importar
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Tab Contents */}
          <TabsContent value="dashboard" className="space-y-6">
            <KPICards kpis={kpis} />
            <SemaforoCriticidad stations={stations} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <EbNoCharts stations={stations} />
              <TrafficCharts stations={stations} />
            </div>
          </TabsContent>

          <TabsContent value="ebno" className="space-y-6">
            <KPICards kpis={kpis} />
            <EbNoCharts stations={stations} />
          </TabsContent>

          <TabsContent value="traffic" className="space-y-6">
            <KPICards kpis={kpis} />
            <TrafficCharts stations={stations} />
          </TabsContent>

          <TabsContent value="stations" className="space-y-6">
            <StationsTable stations={stations} />
          </TabsContent>

          <TabsContent value="tickets" className="space-y-6">
            <TicketManager />
          </TabsContent>

          <TabsContent value="map" className="space-y-6">
            <LocationMap stations={stations} />
          </TabsContent>

          <TabsContent value="opex" className="space-y-6">
            <OpexAnalysis />
          </TabsContent>

          <TabsContent value="upload" className="space-y-6">
            <FileUploader 
              onFileUpload={processExcelFile}
              fileName={fileName}
              loading={loading}
              error={error}
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white mt-8">
        <div className="max-w-[1600px] mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Satellite className="h-4 w-4" />
              <span>DAS Meru Networks - Sistema de Auto-Alimentación NOC-Sync</span>
            </div>
            <div className="flex items-center gap-4">
              <span>Red Satelital VSAT Ku-Band</span>
              <span>•</span>
              <span>50 Estaciones Terrenas</span>
              <span>•</span>
              <span>Spacebridge C7700</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
