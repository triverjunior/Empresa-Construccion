import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
    const router = inject(Router);
    const token = localStorage.getItem('token');

    let role: string | null = null;
    let isTokenExpired = false;

    if (token) {
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if (typeof payload.exp === 'number') {
                const nowInSeconds = Math.floor(Date.now() / 1000);
                if (payload.exp <= nowInSeconds) {
                    isTokenExpired = true;
                }
            }
            role = payload.role;
        } catch (e) {
            localStorage.removeItem('token');
        }
    }

    if (isTokenExpired) {
        localStorage.removeItem('token');
        role = null;
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
