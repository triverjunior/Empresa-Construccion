import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class Globals {
    public apiUrl: string = 'http://localhost:8000/api';
    private http = inject(HttpClient);

    public login(username: string, password: string): Observable<any> {
        const body = new URLSearchParams();
        body.set('username', username);
        body.set('password', password);
        const options = {
            headers: new HttpHeaders().set('Content-Type', 'application/x-www-form-urlencoded')
        };
        return this.http.post(this.apiUrl + '/login', body.toString(), options);
    }

    private getAuthHeaders(): HttpHeaders {
        const token = localStorage.getItem('token');
        return new HttpHeaders().set('Authorization', `Bearer ${token}`);
    }

    public getActiveProject(): Observable<any> {
        return this.http.get(`${this.apiUrl}/active-project`, { headers: this.getAuthHeaders() });
    }

    public createReport(reportData: { project_id: number, title: string, description: string, type: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/reports`, reportData, { headers: this.getAuthHeaders() });
    }
}
