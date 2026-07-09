import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/authService';
import type { LoginForm } from '../types';

interface UseAuthReturn {
  loading: boolean;
  error: string;
  handleLogin: (form: LoginForm) => Promise<void>;
}

export const useAuth = (): UseAuthReturn => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError]     = useState<string>('');
  const navigate              = useNavigate();

  const handleLogin = async (form: LoginForm): Promise<void> => {
    setLoading(true);
    setError('');
    try {
      const data = await login(form);
      localStorage.setItem('token', data.token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('portal_role', data.portal_role ?? data.role);
      localStorage.setItem('username', data.username);
      localStorage.setItem('nombres', data.nombres);
      if (data.id_area != null) {
        localStorage.setItem('id_area', String(data.id_area));
      }
      if (data.area_name) {
        localStorage.setItem('area_name', data.area_name);
      }
      navigate(data.role === 'admin' || data.role === 'area_admin' ? '/admin' : '/dashboard', { replace: true });
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError((err as any).response?.data?.error ?? err.message);
      } else {
        setError('Error al iniciar sesión');
      }
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, handleLogin };
};