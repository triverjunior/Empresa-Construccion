import { Component, inject } from '@angular/core';
import { CommonModule, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Globals } from '../../services/globals';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule, NgClass],
    templateUrl: './login.html',
    styleUrl: './login.css',
})
export class Login {
    public username = '';
    public password = '';
    public errorMessage = '';
    private globals = inject(Globals);
    private router = inject(Router);

    public onSubmit(event: Event): void {
        event.preventDefault();
        this.globals.login(this.username, this.password).subscribe({
            next: (response) => {
                if (response && response.access_token) {
                    const token = response.access_token;
                    localStorage.setItem('token', token);

                    try {
                        const payload = JSON.parse(atob(token.split('.')[1]));
                        if (payload.role === 'admin') {
                            this.router.navigate(['/dashboard']);
                        } else {
                            this.router.navigate(['/mi-trabajo']);
                        }
                    } catch (e) {
                        console.error('Error decoding token');
                    }
                }
            },
            error: (error) => {
                this.errorMessage = 'Invalid username or password';
                console.error(error);
            }
        });
    }
}
