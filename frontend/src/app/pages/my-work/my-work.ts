import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Globals } from '../../services/globals';

interface Project {
    id: number;
    title: string;
    description: string;
    location: string;
}

type ReportType = 'progress' | 'problem';

@Component({
    selector: 'app-my-work',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './my-work.html',
    styleUrl: './my-work.css',
})
export class MyWork implements OnInit {
    private globals = inject(Globals);

    public project = signal<Project | null>(null);
    public isLoading = signal(true);
    public hasProject = signal(false);

    // Form fields
    public reportTitle = '';
    public reportDescription = '';
    public reportType: ReportType = 'progress';

    // UI state
    public isSubmitting = signal(false);
    public successMessage = signal('');
    public errorMessage = signal('');

    ngOnInit(): void {
        this.loadActiveProject();
    }

    private loadActiveProject(): void {
        this.isLoading.set(true);
        this.globals.getActiveProject().subscribe({
            next: (data) => {
                this.project.set(data);
                this.hasProject.set(true);
                this.isLoading.set(false);
            },
            error: () => {
                this.hasProject.set(false);
                this.isLoading.set(false);
            }
        });
    }

    public setReportType(type: ReportType): void {
        this.reportType = type;
    }

    public onSubmitReport(event: Event): void {
        event.preventDefault();
        const proj = this.project();
        if (!proj) return;

        this.isSubmitting.set(true);
        this.successMessage.set('');
        this.errorMessage.set('');

        this.globals.createReport({
            project_id: proj.id,
            title: this.reportTitle,
            description: this.reportDescription,
            type: this.reportType,
        }).subscribe({
            next: () => {
                this.successMessage.set('Reporte enviado correctamente.');
                this.reportTitle = '';
                this.reportDescription = '';
                this.reportType = 'progress';
                this.isSubmitting.set(false);
                setTimeout(() => this.successMessage.set(''), 4000);
            },
            error: () => {
                this.errorMessage.set('Error al enviar el reporte. Inténtalo de nuevo.');
                this.isSubmitting.set(false);
            }
        });
    }
}
