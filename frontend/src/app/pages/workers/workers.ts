import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Globals } from '../../services/globals';

interface Worker {
    id: number;
    username: string;
    email: string;
    disponibility: boolean;
    assigned_project_id: number | null;
}

@Component({
    selector: 'app-workers',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './workers.html',
    styleUrl: './workers.css',
})
export class Workers implements OnInit {
    private globals = inject(Globals);
    private router = inject(Router);

    goBack(): void {
        this.router.navigate(['/dashboard']);
    }

    public workers = signal<Worker[]>([]);
    public isLoading = signal(true);

    public newUsername = '';
    public newEmail = '';
    public newPassword = '';
    public createError = '';
    public createSuccess = '';

    public editingId = signal<number | null>(null);
    public editUsername = '';
    public editEmail = '';
    public editError = '';

    ngOnInit(): void {
        this.loadWorkers();
    }

    private loadWorkers(): void {
        this.isLoading.set(true);
        this.globals.getWorkers().subscribe({
            next: (res) => {
                this.workers.set(res.workers);
                this.isLoading.set(false);
            },
            error: () => this.isLoading.set(false)
        });
    }

    onCreateWorker(event: Event): void {
        event.preventDefault();
        this.createError = '';
        this.createSuccess = '';
        this.globals.createWorker({ username: this.newUsername, email: this.newEmail, password: this.newPassword }).subscribe({
            next: (res) => {
                if (res.error) {
                    this.createError = res.error;
                    return;
                }
                this.createSuccess = 'Worker created successfully.';
                this.newUsername = '';
                this.newEmail = '';
                this.newPassword = '';
                this.loadWorkers();
                setTimeout(() => this.createSuccess = '', 4000);
            },
            error: () => this.createError = 'Error creating worker.'
        });
    }

    startEdit(worker: Worker): void {
        this.editingId.set(worker.id);
        this.editUsername = worker.username;
        this.editEmail = worker.email;
        this.editError = '';
    }

    cancelEdit(): void {
        this.editingId.set(null);
        this.editError = '';
    }

    saveEdit(worker: Worker): void {
        this.editError = '';
        this.globals.updateWorkerData(worker.id, { username: this.editUsername, email: this.editEmail }).subscribe({
            next: () => {
                this.editingId.set(null);
                this.loadWorkers();
            },
            error: () => this.editError = 'Error updating worker.'
        });
    }

    unassign(worker: Worker): void {
        this.globals.unassignWorker(worker.id).subscribe({
            next: () => {
                window.location.reload();
            },
            error: () => {}
        });
    }

    deleteWorker(worker: Worker): void {
        this.globals.deleteWorker(worker.id).subscribe({
            next: () => this.loadWorkers(),
            error: () => {}
        });
    }
}
