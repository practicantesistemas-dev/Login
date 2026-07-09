export interface User {
  username: string;
  role: string;
  token: string;
}

export interface Page {
  id: number;
  name: string;
  ip: string;
  roleId: number;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  role: string;
  username: string;
  nombres: string;
  portal_role?: string;
  id_area?: number | null;
  area_name?: string;
}

export interface UserInfo {
  username: string;
  nombres: string;
  role: string;
  portal_role: string;
  id_area: number | null;
  area_name: string;
  email?: string;
  email_personal?: string;
  email_laboral?: string;
  num_id?: string;
  app_ids?: number[];
}

export interface ProfileUpdatePayload {
  nombres?: string;
  email_personal?: string;
  email_laboral?: string;
  password?: string;
  app_ids?: number[];
}

export interface Department {
  id: number;
  name: string;
}

export interface Application {
  id: number;
  name: string;
  url: string;
  estado: 'activa' | 'inactiva';
  linked_count?: number;
}

export interface ApplicationEstadoResult {
  url: string;
  name: string;
  estado: 'activa' | 'inactiva';
  updated_count: number;
}

export interface ManagedUser {
  id_usuario?: number | null;
  username: string;
  nombres: string;
  num_id: string;
  id_area: number | null;
  area_name: string;
  email_personal: string;
  email_laboral: string;
  portal_role: string;
  report_tipo: string;
  active: boolean;
  app_ids: number[];
}

export interface UserCreatePayload {
  username: string;
  password: string;
  nombres: string;
  num_id: string;
  id_area: number;
  report_tipo: string;
  email_personal?: string;
  email_laboral?: string;
  portal_role?: string;
  app_ids?: number[];
}

export interface UserUpdatePayload {
  password?: string;
  nombres?: string;
  num_id?: string;
  id_area?: number;
  report_tipo?: string;
  email_personal?: string;
  email_laboral?: string;
  portal_role?: string;
  active?: boolean;
  app_ids?: number[];
}

export interface PageLink {
  id: string;
  name: string;
  url: string;
  ip: string;
  icon: string;
  description: string;
}

export interface PageAccessResponse {
  ip: string;
  name: string;
}

export interface ApiError {
  error: string;
}