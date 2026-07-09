import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: '/api',
});

const clearSession = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('portal_role');
  localStorage.removeItem('username');
  localStorage.removeItem('nombres');
  localStorage.removeItem('id_area');
  localStorage.removeItem('area_name');
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status;
    const url: string = error.config?.url ?? '';

    if (status === 401 && !url.includes('/auth/login') && !url.includes('/auth/logout')) {
      clearSession();
      if (window.location.pathname !== '/login') {
        window.location.replace('/login');
      }
    }
    // 403 en SSO: credenciales de app no disponibles; no cerrar sesión del portal
    return Promise.reject(error);
  },
);

export default api;
