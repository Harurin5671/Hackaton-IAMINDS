import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  Kpi,
  ConsumoDiario,
  ConsumoSector,
  Anomalia,
  Recomendacion,
  ApiResponse,
  ChatRequest,
  ChatResponse,
  MlMetrics,
  ForecastPoint
} from './models';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private readonly apiUrl = 'http://localhost:8003/api';

  constructor(private http: HttpClient) { }

  // Get all sedes
  getSedes(): Observable<string[]> {
    return this.http.get<{ sedes: string[] }>(`${this.apiUrl}/sedes`)
      .pipe(map(response => response.sedes));
  }

  // Get KPIs for a specific sede
  getKpis(sede: string): Observable<Kpi> {
    return this.http.get<any>(`${this.apiUrl}/kpis/${sede}`).pipe(
      map(response => ({
        total_kwh: response.total_kwh,
        critical_anomalies: response.anomalías_criticas,
        eficiencia: response.eficiencia,
        meta_eficiencia: response.meta_eficiencia
      }))
    );
  }

  // Get ML Metrics for a specific sede
  getMlMetrics(sede: string): Observable<MlMetrics> {
    return this.http.get<MlMetrics>(`${this.apiUrl}/ml/metrics/${sede}`);
  }

  // Get Forecast for a specific sede
  getForecast(sede: string): Observable<ApiResponse<ForecastPoint[]>> {
    return this.http.get<ApiResponse<ForecastPoint[]>>(`${this.apiUrl}/ml/forecast/${sede}`);
  }

  // Get daily consumption for a specific sede
  getConsumoDiario(sede: string): Observable<ConsumoDiario[]> {
    return this.http.get<ConsumoDiario[]>(`${this.apiUrl}/consumo-diario/${sede}`);
  }

  // Get consumption by sector for a specific sede
  getConsumoSector(sede: string): Observable<ConsumoSector[]> {
    return this.http.get<ConsumoSector[]>(`${this.apiUrl}/consumo-sector/${sede}`);
  }

  // Get anomalies for a specific sede
  getAnomalias(sede: string): Observable<ApiResponse<Anomalia[]>> {
    return this.http.get<ApiResponse<Anomalia[]>>(`${this.apiUrl}/anomalias/${sede}`);
  }

  // Get recommendations for a specific sede
  getRecomendaciones(sede: string): Observable<ApiResponse<Recomendacion[]>> {
    return this.http.get<ApiResponse<Recomendacion[]>>(`${this.apiUrl}/recomendaciones/${sede}`);
  }

  // Chat with AI assistant
  chat(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, request);
  }

  // Check API health
  checkHealth(): Observable<{ message: string; status: string }> {
    return this.http.get<{ message: string; status: string }>(`${this.apiUrl.replace('/api', '')}`);
  }
}
