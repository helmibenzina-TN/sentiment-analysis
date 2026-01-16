import { Routes } from '@angular/router';
import { Login } from './auth/login/login';
import { Register } from './auth/register/register';
import { Dashboard } from './dashboard/dashboard';
import { Results } from './results/results';
import { History } from './history/history';
import { Performance } from './performance/performance';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
    { path: 'login', component: Login },
    { path: 'register', component: Register },
    { path: 'dashboard', component: Dashboard, canActivate: [authGuard] },
    { path: 'results', component: Results, canActivate: [authGuard] },
    { path: 'history', component: History, canActivate: [authGuard] },
    { path: 'performance', component: Performance, canActivate: [authGuard] },
    { path: '**', redirectTo: '/dashboard' }
];
