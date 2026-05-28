import { Component } from '@angular/core';
import { ConfigService } from '../services/config.service';

@Component({
  selector: 'app-home',
  standalone: true,
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  apiUrl = '';

  constructor(private config: ConfigService) {
    this.apiUrl = this.config.apiUrl || '';
  }
}
