import api from './api';
import type { AuthResponse, LoginForm, ProfileUpdatePayload, UserInfo as UserProfileInfo } from '../types';

export interface UserInfo extends UserProfileInfo {}

export const login = async (form: LoginForm): Promise<AuthResponse> => {
  const { data } = await api.post<AuthResponse>('/auth/login', form);
  return data;
};

export const getMe = async (): Promise<UserInfo> => {
  const { data } = await api.get<UserInfo>('/auth/me');
  return data;
};

export const updateMyProfile = async (payload: ProfileUpdatePayload): Promise<UserInfo> => {
  const { data } = await api.put<UserInfo>('/auth/profile', payload);
  return data;
};

export const clearLocalSession = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('portal_role');
  localStorage.removeItem('username');
  localStorage.removeItem('nombres');
  localStorage.removeItem('id_area');
  localStorage.removeItem('area_name');
};

export const logout = async (): Promise<void> => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      await api.post('/auth/logout');
    } catch {
      // Token expirado o inválido: la sesión local se limpia igual
    }
  }
  clearLocalSession();
};

export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('token');
  return !!token && token.split('.').length === 3;
};

export const verifySession = async (): Promise<boolean> => {
  if (!isAuthenticated()) {
    clearLocalSession();
    return false;
  }

  try {
    const user = await getMe();
    localStorage.setItem('role', user.role);
    localStorage.setItem('portal_role', user.portal_role ?? user.role);
    localStorage.setItem('username', user.username);
    localStorage.setItem('nombres', user.nombres);
    if (user.id_area != null) {
      localStorage.setItem('id_area', String(user.id_area));
    }
    if (user.area_name) {
      localStorage.setItem('area_name', user.area_name);
    }
    return true;
  } catch {
    clearLocalSession();
    return false;
  }
};

export const launchApp = async (url: string): Promise<void> => {
  const { data } = await api.post<string>('/sso/launch', { url }, {
    responseType: 'text',
  });

  const win = window.open('', '_blank');
  if (!win) {
    throw new Error('El navegador bloqueó la ventana emergente.');
  }

  win.document.open();
  win.document.write(data);
  win.document.close();
};

export const isAdminRole = (): boolean => {
  const role = localStorage.getItem('portal_role') ?? localStorage.getItem('role');
  return role === 'admin' || role === 'area_admin';
};

export const getPortalRole = (): string => {
  return localStorage.getItem('portal_role') ?? localStorage.getItem('role') ?? 'usuario';
};
