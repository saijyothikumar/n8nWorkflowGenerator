import { Injectable } from '@angular/core';

export interface AppConfig {
  apiUrl?: string;
  [key: string]: unknown;
}

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private config: AppConfig | null = null;

  set(config: AppConfig) {
    this.config = config;
  }

  get apiUrl(): string {
    const url = this.config?.apiUrl;
    return typeof url === 'string' ? url.trim().replace(/\/+$|\s+$/g, '') : '';
  }
}
