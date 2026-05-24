import { Component } from '@angular/core';

import { ChatPanelComponent } from './chat-panel.component';
import { GraphPanelComponent } from './graph-panel.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatPanelComponent, GraphPanelComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {}
