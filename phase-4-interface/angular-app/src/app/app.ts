import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Dashboard } from './pages/dashboard/dashboard';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Dashboard],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('angular-app');
}
