import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { MyWork } from './pages/my-work/my-work';
import { Dashboard } from './pages/dashboard/dashboard';
import { Projects } from './pages/projects/projects';
import { Workers } from './pages/workers/workers';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    { path: 'iniciar-sesion', component: Login, canActivate: [authGuard] },
    { path: 'mi-trabajo', component: MyWork, canActivate: [authGuard] },
    { path: 'dashboard', component: Dashboard, canActivate: [authGuard] },
    { path: 'trabajadores', component: Workers, canActivate: [authGuard] },
    { path: 'obras', component: Projects, canActivate: [authGuard] },
    { path: '**', redirectTo: 'iniciar-sesion' }
];
