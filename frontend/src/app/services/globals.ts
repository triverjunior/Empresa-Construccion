import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root',
})
export class Globals {
    public apiUrl: string = 'https://empresa-construccion-production.up.railway.app/api';
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

    public getWorkers(): Observable<any> {
        return this.http.get(`${this.apiUrl}/workers`, { headers: this.getAuthHeaders() });
    }

    public createWorker(data: { username: string, email: string, password: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/register`, { ...data, role: 'worker' }, { headers: this.getAuthHeaders() });
    }

    public updateWorkerData(id: number, data: { username: string, email: string }): Observable<any> {
        return this.http.put(`${this.apiUrl}/workers/${id}/data`, data, { headers: this.getAuthHeaders() });
    }

    public unassignWorker(id: number): Observable<any> {
        return this.http.put(`${this.apiUrl}/workers/${id}/disponibility`, { disponibility: true, assigned_project_id: 0 }, { headers: this.getAuthHeaders() });
    }

    public deleteWorker(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/workers/${id}`, { headers: this.getAuthHeaders() });
    }

    public getProjects(): Observable<any> {
        return this.http.get(`${this.apiUrl}/projects`, { headers: this.getAuthHeaders() });
    }

    public createProject(data: { title: string, description: string, location: string }): Observable<any> {
        return this.http.post(`${this.apiUrl}/projects`, data, { headers: this.getAuthHeaders() });
    }

    public updateProject(id: number, data: { title: string, description: string, location: string }): Observable<any> {
        return this.http.put(`${this.apiUrl}/projects/${id}`, data, { headers: this.getAuthHeaders() });
    }

    public deleteProject(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/projects/${id}`, { headers: this.getAuthHeaders() });
    }

    public getReports(): Observable<any> {
        return this.http.get(`${this.apiUrl}/reports`, { headers: this.getAuthHeaders() });
    }

    public assignWorkerToProject(workerId: number, projectId: number): Observable<any> {
        return this.http.put(`${this.apiUrl}/workers/${workerId}/disponibility`, { disponibility: false, assigned_project_id: projectId }, { headers: this.getAuthHeaders() });
    }
}
