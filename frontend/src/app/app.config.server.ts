import { mergeApplicationConfig, ApplicationConfig, provideAppInitializer, inject } from '@angular/core';
import { provideServerRendering, withRoutes } from '@angular/ssr';
import { appConfig } from './app.config';
import { serverRoutes } from './app.routes.server';
import { ConfigService } from './services/config.service';

const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering(withRoutes(serverRoutes)),
    provideAppInitializer(() => {
      const config = inject(ConfigService);
      // Use environment variable on the server to avoid HTTP fetch during prerender.
      config.set({ apiUrl: process.env['API_URL'] || '' });
    })
  ]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
