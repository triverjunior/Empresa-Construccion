import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Globals } from '../../services/globals';

interface Project {
    id: number;
    title: string;
    description: string;
    location: string;
}

interface Worker {
    id: number;
    username: string;
    email: string;
    disponibility: boolean;
    assigned_project_id: number | null;
}

interface Report {
    id: number;
    user_id: number;
    project_id: number;
    title: string;
    description: string;
    type: string;
}

@Component({
    selector: 'app-projects',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './projects.html',
    styleUrl: './projects.css',
})
export class Projects implements OnInit {
    private globals = inject(Globals);
    private router = inject(Router);

    public projects = signal<Project[]>([]);
    public workers = signal<Worker[]>([]);
    public isLoading = signal(true);

    public newTitle = '';
    public newDescription = '';
    public newLocation = '';
    public createError = '';
    public createSuccess = '';

    public editingId = signal<number | null>(null);
    public editTitle = '';
    public editDescription = '';
    public editLocation = '';
    public editError = '';

    public assigningProjectId = signal<number | null>(null);
    public selectedWorkerId: number | null = null;
    public assignError = '';

    public viewingReportsId = signal<number | null>(null);
    public allReports = signal<Report[]>([]);
    public reportsLoading = signal(false);

    reportsForProject(projectId: number): Report[] {
        return this.allReports().filter(r => r.project_id === projectId);
    }

    goBack(): void {
        this.router.navigate(['/dashboard']);
    }

    ngOnInit(): void {
        this.loadProjects();
        this.loadWorkers();
        this.loadReports();
    }

    private loadProjects(): void {
        this.isLoading.set(true);
        this.globals.getProjects().subscribe({
            next: (res) => {
                this.projects.set(res.projects);
                this.isLoading.set(false);
            },
            error: () => this.isLoading.set(false)
        });
    }

    private loadWorkers(): void {
        this.globals.getWorkers().subscribe({
            next: (res) => this.workers.set(res.workers),
            error: () => {}
        });
    }

    private loadReports(): void {
        this.reportsLoading.set(true);
        this.globals.getReports().subscribe({
            next: (res) => {
                this.allReports.set(res.reports);
                this.reportsLoading.set(false);
            },
            error: () => this.reportsLoading.set(false)
        });
    }

    toggleReports(projectId: number): void {
        if (this.viewingReportsId() === projectId) {
            this.viewingReportsId.set(null);
        } else {
            this.viewingReportsId.set(projectId);
            this.editingId.set(null);
            this.assigningProjectId.set(null);
        }
    }

    availableWorkers(): Worker[] {
        return this.workers().filter(w => w.disponibility && !w.assigned_project_id);
    }

    onCreateProject(event: Event): void {
        event.preventDefault();
        this.createError = '';
        this.createSuccess = '';
        this.globals.createProject({ title: this.newTitle, description: this.newDescription, location: this.newLocation }).subscribe({
            next: () => {
                this.createSuccess = 'Project created successfully.';
                this.newTitle = '';
                this.newDescription = '';
                this.newLocation = '';
                this.loadProjects();
                setTimeout(() => this.createSuccess = '', 4000);
            },
            error: (err) => {
                this.createError = err?.error?.detail ?? 'Error creating project.';
            }
        });
    }

    startEdit(project: Project): void {
        this.editingId.set(project.id);
        this.editTitle = project.title;
        this.editDescription = project.description;
        this.editLocation = project.location;
        this.editError = '';
        this.assigningProjectId.set(null);
        this.viewingReportsId.set(null);
    }

    cancelEdit(): void {
        this.editingId.set(null);
        this.editError = '';
    }

    saveEdit(project: Project): void {
        this.editError = '';
        this.globals.updateProject(project.id, { title: this.editTitle, description: this.editDescription, location: this.editLocation }).subscribe({
            next: () => {
                this.editingId.set(null);
                this.loadProjects();
            },
            error: (err) => {
                this.editError = err?.error?.detail ?? 'Error updating project.';
            }
        });
    }

    deleteProject(project: Project): void {
        this.globals.deleteProject(project.id).subscribe({
            next: () => this.loadProjects(),
            error: () => {}
        });
    }

    startAssign(projectId: number): void {
        this.assigningProjectId.set(projectId);
        this.selectedWorkerId = null;
        this.assignError = '';
        this.editingId.set(null);
        this.viewingReportsId.set(null);
    }

    cancelAssign(): void {
        this.assigningProjectId.set(null);
        this.assignError = '';
    }

    confirmAssign(): void {
        if (!this.selectedWorkerId || !this.assigningProjectId()) return;
        this.globals.assignWorkerToProject(this.selectedWorkerId, this.assigningProjectId()!).subscribe({
            next: () => {
                this.assigningProjectId.set(null);
                this.loadWorkers();
                this.loadProjects();
            },
            error: () => this.assignError = 'Error assigning worker.'
        });
    }
}
