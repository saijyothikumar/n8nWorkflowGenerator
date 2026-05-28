import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface N8NConnectionState {
  baseUrl: string;
  apiKey: string;
  connected: boolean;
  nodeTypesCount: number;
  errorMessage: string;
  loading: boolean;
}

@Injectable({ providedIn: 'root' })
export class N8NConnectionService {
  state: N8NConnectionState = {
    baseUrl: '',
    apiKey: '',
    connected: false,
    nodeTypesCount: 0,
    errorMessage: '',
    loading: false,
  };

  constructor(private http: HttpClient) {}

  async connect(n8nUrl: string, apiKey: string): Promise<boolean> {
    this.state.loading = true;
    this.state.errorMessage = '';
    this.state.connected = false;
    this.state.nodeTypesCount = 0;
    this.state.baseUrl = n8nUrl.trim().replace(/\/+$|\s+$/, '');
    this.state.apiKey = apiKey;

    try {
      const result = await firstValueFrom(
        this.http.post<any>('/api/n8n/connect', {
          n8n_url: this.state.baseUrl,
          api_key: this.state.apiKey,
        })
      );

      if (!result?.success) {
        this.state.errorMessage = this._formatError(result?.error) || 'Unable to connect to n8n';
        return false;
      }

      this.state.connected = true;
      void this._loadNodeTypesInBackground();
      return true;
    } catch (error: any) {
      this.state.errorMessage = error?.message || 'Connection failed';
      return false;
    } finally {
      this.state.loading = false;
    }
  }

  async loadNodeTypes(): Promise<any> {
    return firstValueFrom(this.http.get<any>('/api/n8n/node-types'));
  }

  async getNodeCategories(): Promise<any> {
    return firstValueFrom(this.http.get<any>('/api/n8n/node-categories'));
  }

  private async _loadNodeTypesInBackground(): Promise<void> {
    try {
      const nodeTypesResult = await this.loadNodeTypes();
      if (!nodeTypesResult?.success) {
        this.state.errorMessage = this._formatError(nodeTypesResult?.error) || 'Connected but failed to load node types';
        return;
      }
      this.state.nodeTypesCount = this._extractNodeTypesCount(nodeTypesResult.data);
    } catch (error: unknown) {
      this.state.errorMessage = this._formatError(error);
    }
  }

  private _extractNodeTypesCount(data: unknown): number {
    if (Array.isArray(data)) {
      return data.length;
    }
    if (data && typeof data === 'object' && 'data' in (data as any) && Array.isArray((data as any).data)) {
      return (data as any).data.length;
    }
    return 0;
  }

  private _formatError(error: unknown): string {
    if (!error) {
      return '';
    }
    if (typeof error === 'string') {
      return error;
    }
    try {
      return JSON.stringify(error);
    } catch {
      return String(error);
    }
  }
}
