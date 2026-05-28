import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { N8NConnectionService } from '../services/n8n-connection.service';

@Component({
  selector: 'app-settings-connection',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings-connection.component.html',
  styleUrls: ['./settings-connection.component.css'],
})
export class SettingsConnectionComponent {
  drawerOpen = false;
  n8nUrl = '';
  apiKey = '';

  constructor(public connection: N8NConnectionService) {}

  async connect(): Promise<void> {
    if (!this.n8nUrl || !this.apiKey) {
      this.connection.state.errorMessage = 'Both N8N URL and API key are required.';
      return;
    }

    await this.connection.connect(this.n8nUrl, this.apiKey);
    if (this.connection.state.connected) {
      this.drawerOpen = false;
    }
  }

  toggleDrawer(): void {
    this.drawerOpen = !this.drawerOpen;
    this.connection.state.errorMessage = '';
  }
}
