import { ApplicationConfig, provideBrowserGlobalErrorListeners, inject } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { provideHttpClient, HttpClient, withFetch } from '@angular/common/http';
import { provideAppInitializer } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { ConfigService, AppConfig as RuntimeConfig } from './services/config.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideClientHydration(withEventReplay()),
    provideHttpClient(withFetch()),
    provideAppInitializer(() => {
      const cfg = inject(ConfigService);
      // If running on the server (prerender / SSR), skip the network fetch to avoid timeouts
      if (typeof window === 'undefined') {
        cfg.set({});
        return Promise.resolve();
      }
      const http = inject(HttpClient);
      const loadPromise = firstValueFrom(http.get<RuntimeConfig>('/assets/config.json'))
        .then((c) => cfg.set(c))
        .catch(() => {});
      // Prevent long hangs during prerender or network issues by racing a short timeout
      const timeout = new Promise((res) => setTimeout(res, 2000));
      return Promise.race([loadPromise, timeout]);
    })
  ]
};
