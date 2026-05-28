import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, HttpClient, withFetch } from '@angular/common/http';
import { provideAppInitializer, inject, ApplicationConfig } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { appConfig } from './app/app.config';
import { App } from './app/app';
import { ConfigService } from './app/services/config.service';

const browserInit = provideAppInitializer(async () => {
  const http = inject(HttpClient);
  const config = inject(ConfigService);
  const res = await firstValueFrom(http.get('/assets/config.json'));
  return config.set(res as any);
});

const bootstrapConfig: ApplicationConfig = {
  ...appConfig,
  providers: [
    ...(appConfig.providers ?? []),
    provideHttpClient(withFetch()),
    browserInit,
  ],
};

bootstrapApplication(App, bootstrapConfig).catch((err) => console.error(err));
