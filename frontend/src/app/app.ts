import { Component, isDevMode } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { RouterOutlet } from '@angular/router';

import { ChatPanelComponent } from './chat-panel/chat-panel.component';
import { GraphPanelComponent } from './graph-panel/graph-panel.component';
import { SettingsConnectionComponent } from './settings-connection/settings-connection.component';
import { ConfigService } from './services/config.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatPanelComponent, GraphPanelComponent, SettingsConnectionComponent, HttpClientModule, RouterOutlet],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  constructor(private http: HttpClient, private config: ConfigService) {
    if (!isDevMode()) {
      const base = (this.config.apiUrl || '').trim();
      const healthUrl = base ? base.replace(/\/+$/, '') + '/health' : '/health';
      setInterval(() => this.http.get(healthUrl).subscribe({ next: () => {}, error: () => {} }), 10 * 60 * 1000);
    }
  }
}
