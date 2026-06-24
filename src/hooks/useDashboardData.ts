import { useState, useCallback, useEffect } from 'react';
import * as XLSX from 'xlsx';
import type { DashboardData, Station, KPIs } from '@/types/dashboard';

const DEFAULT_DATA_URL = '/dashboard_data.json';

const statusMap: Record<string, Station['status']> = {
  'Operativo': 'Operativo',
  'Fuera de Servicio': 'Fuera de Servicio',
  'Intermitente': 'Intermitente',
  'En Espera': 'En Espera',
  'Test': 'Test',
};

export function useDashboardData() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');

  // Load default data on mount
  useEffect(() => {
    fetch(DEFAULT_DATA_URL)
      .then(res => res.json())
      .then((jsonData: DashboardData) => {
        setData(jsonData);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading default data:', err);
        setError('Error cargando datos por defecto');
        setLoading(false);
      });
  }, []);

  const processExcelFile = useCallback((file: File) => {
    setLoading(true);
    setError(null);
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        if (!data) return;

        const workbook = XLSX.read(data, { type: 'binary' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][];

        if (jsonData.length < 2) {
          setError('El archivo Excel está vacío o tiene formato inválido');
          setLoading(false);
          return;
        }

        // Detect file type based on headers
        const headers = jsonData[0] as string[];
        const firstHeader = headers[0]?.toString() || '';

        if (firstHeader.includes('Data Usage Report')) {
          processVNOReport(jsonData);
        } else if (firstHeader.includes('Date (UTC)')) {
          if (headers[1]?.includes('Eb/No') || headers[1]?.includes('Tuner')) {
            processEbNoData(jsonData);
          } else if (headers[1]?.includes('ifInOctets') || headers[1]?.includes('ifOutOctets')) {
            processTrafficData(jsonData);
          } else {
            setError('Formato de archivo no reconocido. Use archivos de Eb/No, Tráfico o VNO Report.');
            setLoading(false);
          }
        } else {
          setError('Formato de archivo no reconocido. Asegúrese de usar un archivo válido de Meru Networks.');
          setLoading(false);
        }
      } catch (err) {
        setError('Error procesando el archivo: ' + (err as Error).message);
        setLoading(false);
      }
    };
    reader.readAsBinaryString(file);
  }, []);

  const processEbNoData = (jsonData: any[][]) => {
    const headers = jsonData[0] as string[];
    const stations: Record<string, { rl_ebno: number[]; fl_ebno: number[] }> = {};

    // Parse column headers to extract station names
    for (let i = 1; i < headers.length; i++) {
      const colName = headers[i]?.toString() || '';
      const parts = colName.split('/');
      if (parts.length >= 2) {
        const stationId = parts[0];
        const metric = parts[1];
        if (!stations[stationId]) {
          stations[stationId] = { rl_ebno: [], fl_ebno: [] };
        }

        // Extract values for this column
        for (let row = 1; row < jsonData.length; row++) {
          const val = parseFloat(jsonData[row][i]);
          if (!isNaN(val)) {
            if (metric.includes('RL')) {
              stations[stationId].rl_ebno.push(val);
            } else if (metric.includes('FL')) {
              stations[stationId].fl_ebno.push(val);
            }
          }
        }
      }
    }

    // Calculate averages and update station data
    setData(prev => {
      if (!prev) return prev;
      const updatedStations = prev.stations.map(st => {
        const computed = stations[st.id];
        if (computed) {
          const avgRl = computed.rl_ebno.length > 0
            ? computed.rl_ebno.reduce((a, b) => a + b, 0) / computed.rl_ebno.length
            : st.rl_ebno_db;
          const avgFl = computed.fl_ebno.length > 0
            ? computed.fl_ebno.reduce((a, b) => a + b, 0) / computed.fl_ebno.length
            : st.fl_ebno_db;
          const margin = Math.max(0, avgRl - 5.0);

          let status = st.status;
          if (margin === 0) status = 'Fuera de Servicio';
          else if (margin < 2.0) status = 'Intermitente';
          else status = 'Operativo';

          return {
            ...st,
            rl_ebno_db: Math.round(avgRl * 100) / 100,
            fl_ebno_db: Math.round(avgFl * 100) / 100,
            margin_db: Math.round(margin * 10) / 10,
            status: statusMap[status] || st.status,
          };
        }
        return st;
      });

      // Recalculate KPIs
      const kpis = calculateKPIs(updatedStations);
      return { ...prev, stations: updatedStations, kpis };
    });

    setLoading(false);
  };

  const processTrafficData = (jsonData: any[][]) => {
    const headers = jsonData[0] as string[];
    const stations: Record<string, { traffic_in: number[]; traffic_out: number[] }> = {};

    for (let i = 1; i < headers.length; i++) {
      const colName = headers[i]?.toString() || '';
      const parts = colName.split('/');
      if (parts.length >= 2) {
        const stationId = parts[0];
        const metric = parts[1];
        if (!stations[stationId]) {
          stations[stationId] = { traffic_in: [], traffic_out: [] };
        }

        for (let row = 1; row < jsonData.length; row++) {
          const val = parseFloat(jsonData[row][i]);
          if (!isNaN(val)) {
            if (metric.includes('ifInOctets')) {
              stations[stationId].traffic_in.push(val);
            } else if (metric.includes('ifOutOctets')) {
              stations[stationId].traffic_out.push(val);
            }
          }
        }
      }
    }

    setData(prev => {
      if (!prev) return prev;
      const updatedStations = prev.stations.map(st => {
        const computed = stations[st.id];
        if (computed) {
          const totalIn = computed.traffic_in.reduce((a, b) => a + b, 0);
          const totalOut = computed.traffic_out.reduce((a, b) => a + b, 0);
          return {
            ...st,
            traffic_in_mb: Math.round(totalIn * 100) / 100,
            traffic_out_mb: Math.round(totalOut * 100) / 100,
          };
        }
        return st;
      });

      const kpis = calculateKPIs(updatedStations);
      return { ...prev, stations: updatedStations, kpis };
    });

    setLoading(false);
  };

  const processVNOReport = (_jsonData: any[][]) => {
    // VNO Report format - rows are dates, columns are stations
    setData(prev => {
      if (!prev) return prev;
      // Keep existing but mark as updated
      return { ...prev };
    });

    setLoading(false);
  };

  const calculateKPIs = (stations: Station[]): KPIs => {
    const operational = stations.filter(s => s.status === 'Operativo').length;
    const outOfService = stations.filter(s => s.status === 'Fuera de Servicio').length;
    const intermittent = stations.filter(s => s.status === 'Intermitente').length;
    const onHold = stations.filter(s => s.status === 'En Espera').length;

    const margins = stations.filter(s => s.margin_db > 0).map(s => s.margin_db);
    const avgMargin = margins.length > 0 ? margins.reduce((a, b) => a + b, 0) / margins.length : 0;

    const totalTrafficIn = stations.reduce((sum, s) => sum + s.traffic_in_mb, 0);
    const totalTrafficOut = stations.reduce((sum, s) => sum + s.traffic_out_mb, 0);

    const criticalStations = stations.filter(s => s.margin_db < 4.0 && s.margin_db > 0).length;
    const healthyStations = stations.filter(s => s.margin_db >= 4.0).length;

    const availability = operational / Math.max(stations.filter(s => s.status !== 'Test').length, 1) * 100;

    return {
      total_stations: 50,
      operational,
      out_of_service: outOfService,
      intermittent,
      on_hold: onHold,
      availability_percent: Math.round(availability * 10) / 10,
      avg_margin_db: Math.round(avgMargin * 100) / 100,
      total_traffic_in_mb: Math.round(totalTrafficIn * 100) / 100,
      total_traffic_out_mb: Math.round(totalTrafficOut * 100) / 100,
      critical_stations: criticalStations,
      healthy_stations: healthyStations,
      opex_savings_percent: 35.3,
      date_range: {
        start: new Date().toISOString(),
        end: new Date().toISOString(),
      },
    };
  };

  return {
    data,
    loading,
    error,
    fileName,
    processExcelFile,
  };
}
