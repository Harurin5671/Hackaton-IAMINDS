export interface Kpi {
  total_kwh: number;
  critical_anomalies: number;
  eficiencia: number;
  meta_eficiencia: number;
}

export interface ConsumoDiario {
  timestamp: string;
  energia_total_kwh: number;
}

export interface ConsumoSector {
  timestamp: string;
  sector: string;
  kWh: number;
}

export interface Anomalia {
  timestamp: string;
  energia_total_kwh: number;
  ocupacion_pct: number;
  anomaly_critical: number;
  sede: string;
}

export interface Recomendacion {
  event_id?: number;
  category?: string;
  duration_hours?: number;
  avg_occupancy?: number;
  total_kwh?: number;
  sede?: string;
  ai_recommendation?: string;
  start_time?: string;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface ChatRequest {
  sede: string;
  pregunta: string;
}

export interface ChatResponse {
  respuesta?: string;
  error?: string;
}

export interface InefficientSector {
  sede: string;
  sector_nombre: string;
  intensidad_kwh_hora: number;
  desperdicio_kwh: number;
  '%_desviaje': number;
}

export interface CriticalHour {
  sector: string;
  peak_hour: number;
  avg_consumption: number;
}

export interface RecentAnomaly {
  timestamp: string;
  sede: string;
  sector_nombre: string;
  consumo_kwh: number;
  es_pico_anomalo: boolean;
  error: number;
  timestamp_str: string;
}

export interface WasteStats {
  total_waste_kwh: number;
  worst_sector: string;
}

export interface InefficiencyAnalysis {
  inefficient_sectors_ranking: InefficientSector[];
  critical_hours: CriticalHour[];
  recent_anomalies: RecentAnomaly[];
  waste_stats: WasteStats;
  error?: string;
}
