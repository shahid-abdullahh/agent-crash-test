import type {
  Task,
  Run,
  RunCreateRequest,
  TraceEvent,
  EvaluationResult,
  DiagnosisResult,
  ReliabilityOverview,
  HealthCheckResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          ...(options?.headers || {}),
        },
        ...options,
      });

      if (!response.ok) {
        let errorDetail = response.statusText;
        try {
          const errJson = await response.json();
          errorDetail = errJson.detail || JSON.stringify(errJson);
        } catch {
          // fallback to status text
        }
        throw new Error(`API Error [${response.status}] ${endpoint}: ${errorDetail}`);
      }

      return await response.json();
    } catch (err: any) {
      console.error(`Fetch failed for ${url}:`, err);
      throw err;
    }
  }

  async getHealth(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/health');
  }

  async getTasks(): Promise<Task[]> {
    return this.request<Task[]>('/tasks');
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`/tasks/${taskId}`);
  }

  async createAndExecuteRun(payload: RunCreateRequest): Promise<Run> {
    return this.request<Run>('/runs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getRun(runId: string): Promise<Run> {
    return this.request<Run>(`/runs/${runId}`);
  }

  async getRunTrace(runId: string): Promise<TraceEvent[]> {
    return this.request<TraceEvent[]>(`/runs/${runId}/trace`);
  }

  async getRunEvaluation(runId: string): Promise<EvaluationResult> {
    return this.request<EvaluationResult>(`/runs/${runId}/evaluation`);
  }

  async getRunDiagnosis(runId: string): Promise<DiagnosisResult | null> {
    return this.request<DiagnosisResult | null>(`/runs/${runId}/diagnosis`);
  }

  async getReliability(): Promise<ReliabilityOverview> {
    return this.request<ReliabilityOverview>('/reliability');
  }

  async getComparison(baselineRunId: string, remediatedRunId: string): Promise<any> {
    return this.request(`/comparison?baseline_run_id=${baselineRunId}&remediated_run_id=${remediatedRunId}`);
  }

  async getIntegrations(): Promise<any[]> {
    return this.request('/integrations');
  }

  async getIntegration(id: string): Promise<any> {
    return this.request(`/integrations/${id}`);
  }

  async importIntegration(payload: { name: string; spec_url?: string; spec_content?: string }): Promise<any> {
    return this.request('/integrations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getIntegrationCode(id: string): Promise<Record<string, string>> {
    return this.request(`/integrations/${id}/code`);
  }

  async getConnectors(): Promise<any[]> {
    return this.request('/connectors');
  }

  async getDocumentation(integrationId: string): Promise<any> {
    return this.request(`/documentation/${integrationId}`);
  }

  async resetDemoEnvironment(): Promise<any> {
    return this.request('/admin/demo/reset', { method: 'POST' });
  }
}

export const api = new ApiService();
