import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

interface LoginResponse {
    token: string;
    user: {
        name: string;
        role: string;
        avatar: string;
    };
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api/auth/login';

    // Signal to track user state
    currentUser = signal<any>(null);

    constructor(private http: HttpClient, private router: Router) {
        // Restore session
        const savedUser = localStorage.getItem('indra_user');
        if (savedUser) {
            this.currentUser.set(JSON.parse(savedUser));
        }
    }

    login(credentials: { username: string, password: string }): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(this.apiUrl, credentials).pipe(
            tap(response => {
                localStorage.setItem('indra_token', response.token);
                localStorage.setItem('indra_user', JSON.stringify(response.user));
                this.currentUser.set(response.user);
            })
        );
    }

    logout() {
        localStorage.removeItem('indra_token');
        localStorage.removeItem('indra_user');
        this.currentUser.set(null);
        this.router.navigate(['/login']);
    }

    isLoggedIn(): boolean {
        return !!localStorage.getItem('indra_token');
    }
}
