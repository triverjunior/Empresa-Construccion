import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
    const router = inject(Router);
    const token = localStorage.getItem('token');

    let role: string | null = null;

    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            role = payload.role;
        } catch (e) {
            localStorage.removeItem('token');
        }
    }

    const url = state.url.split('?')[0];

    if (!role) {
        if (url === '/iniciar-sesion') {
            return true;
        }
        return router.createUrlTree(['/iniciar-sesion']);
    }

    if (role === 'worker') {
        if (url === '/mi-trabajo') {
            return true;
        }
        return router.createUrlTree(['/mi-trabajo']);
    }

    if (role === 'admin') {
        if (url === '/dashboard' || url === '/trabajadores' || url === '/obras') {
            return true;
        }
        return router.createUrlTree(['/dashboard']);
    }

    return router.createUrlTree(['/iniciar-sesion']);
};
