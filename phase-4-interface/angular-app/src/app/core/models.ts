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
