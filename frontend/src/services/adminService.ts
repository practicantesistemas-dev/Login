import api from './api';
import type {
  Application,
  ApplicationEstadoResult,
  Department,
  ManagedUser,
  UserCreatePayload,
  UserUpdatePayload,
} from '../types';

export const getDepartments = async (): Promise<Department[]> => {
  const { data } = await api.get<Department[]>('/admin/departments');
  return data;
};

export const getApplications = async (estado?: 'activa' | 'inactiva'): Promise<Application[]> => {
  const { data } = await api.get<Application[]>('/admin/applications', {
    params: estado ? { estado } : undefined,
  });
  return data;
};

export interface UserListFilters {
  id_area?: number;
  q?: string;
}

export const getManagedUsers = async (filters?: UserListFilters): Promise<ManagedUser[]> => {
  const { data } = await api.get<ManagedUser[]>('/admin/users', { params: filters });
  return data;
};

export const createManagedUser = async (payload: UserCreatePayload): Promise<ManagedUser> => {
  const { data } = await api.post<ManagedUser>('/admin/users', payload);
  return data;
};

export const updateManagedUser = async (
  username: string,
  payload: UserUpdatePayload,
): Promise<ManagedUser> => {
  const { data } = await api.put<ManagedUser>(`/admin/users/${encodeURIComponent(username)}`, payload);
  return data;
};

export const deactivateManagedUser = async (username: string): Promise<ManagedUser> => {
  const { data } = await api.post<ManagedUser>(
    `/admin/users/${encodeURIComponent(username)}/deactivate`,
  );
  return data;
};

export const setApplicationEstado = async (
  url: string,
  estado: 'activa' | 'inactiva',
): Promise<ApplicationEstadoResult> => {
  const { data } = await api.patch<ApplicationEstadoResult>('/admin/applications/estado', {
    url,
    estado,
  });
  return data;
};
