import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { ConfigService } from './config.service';

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
  private readonly STORAGE_KEY = 'n8n_credentials';

  state: N8NConnectionState = {
    baseUrl: '',
    apiKey: '',
    connected: false,
    nodeTypesCount: 0,
    errorMessage: '',
    loading: false,
  };

  constructor(
    private http: HttpClient,
    private configService: ConfigService
  ) {}

  /**
   * Persist credentials to sessionStorage after successful connection
   */
  private _saveCredentials(baseUrl: string, apiKey: string): void {
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem(
        this.STORAGE_KEY,
        JSON.stringify({ baseUrl, apiKey })
      );
    }
  }

  /**
   * Load credentials from sessionStorage
   */
  private _loadCachedCredentials(): { baseUrl: string; apiKey: string } | null {
    if (typeof sessionStorage === 'undefined') {
      return null;
    }
    try {
      const cached = sessionStorage.getItem(this.STORAGE_KEY);
      return cached ? JSON.parse(cached) : null;
    } catch {
      return null;
    }
  }

  /**
   * Attempt to auto-reconnect using cached credentials (called on app startup)
   */
  async autoReconnect(): Promise<boolean> {
    const cached = this._loadCachedCredentials();
    if (!cached || !cached.baseUrl || !cached.apiKey) {
      return false;
    }

    // Silently try to reconnect without showing loading state or errors
    try {
      const result = await firstValueFrom(
        this.http.post<any>(`${this.configService.apiUrl}/api/n8n/connect`, {
          n8n_url: cached.baseUrl,
          api_key: cached.apiKey,
        })
      );

      if (result?.success) {
        this.state.baseUrl = cached.baseUrl;
        this.state.apiKey = cached.apiKey;
        this.state.connected = true;
        void this._loadNodeTypesInBackground();
        return true;
      }
    } catch {
      // Silently fail; user will be prompted to reconnect if needed
    }
    return false;
  }

  async connect(n8nUrl: string, apiKey: string): Promise<boolean> {
    this.state.loading = true;
    this.state.errorMessage = '';
    this.state.connected = false;
    this.state.nodeTypesCount = 0;
    this.state.baseUrl = n8nUrl.trim().replace(/\/+$|\s+$/, '');
    this.state.apiKey = apiKey;

    try {
      const result = await firstValueFrom(
        this.http.post<any>(`${this.configService.apiUrl}/api/n8n/connect`, {
          n8n_url: this.state.baseUrl,
          api_key: this.state.apiKey,
        })
      );

      if (!result?.success) {
        this.state.errorMessage = this._formatError(result?.error) || 'Unable to connect to n8n';
        return false;
      }

      this.state.connected = true;
      // Save credentials on successful connection
      this._saveCredentials(this.state.baseUrl, this.state.apiKey);
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
    return firstValueFrom(this.http.get<any>(`${this.configService.apiUrl}/api/n8n/node-types`));
  }

  async getNodeCategories(): Promise<any> {
    return firstValueFrom(this.http.get<any>(`${this.configService.apiUrl}/api/n8n/node-categories`));
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
