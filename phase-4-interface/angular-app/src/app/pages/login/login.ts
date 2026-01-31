import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './login.html',
    styleUrl: './login.css'
})
export class Login {
    username = '';
    password = '';
    loading = signal(false);
    error = signal('');

    constructor(private auth: AuthService, private router: Router) { }

    onLogin(event: Event) {
        event.preventDefault();
        if (!this.username || !this.password) {
            this.error.set('Por favor completa todos los campos');
            return;
        }

        this.loading.set(true);
        this.error.set('');

        this.auth.login({ username: this.username, password: this.password }).subscribe({
            next: () => {
                this.loading.set(false);
                this.router.navigate(['/dashboard']);
            },
            error: (err) => {
                this.loading.set(false);
                this.error.set(err.error?.detail || 'Error de autenticación');
            }
        });
    }
}
