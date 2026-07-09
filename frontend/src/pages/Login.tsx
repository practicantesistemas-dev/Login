import React, { useEffect, useState } from 'react';
import { login } from '../services/authService';
import type { LoginForm } from '../types';

interface LoginProps {
  onLoginSuccess: () => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [form, setForm] = useState<LoginForm>({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const savedUsername = localStorage.getItem('last_username');
    if (savedUsername) {
      setForm(prev => ({ ...prev, username: savedUsername }));
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      localStorage.setItem('last_username', form.username.trim());
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
      onLoginSuccess();
      const destination =
        data.role === 'admin' || data.role === 'area_admin' ? '/admin' : '/dashboard';
      window.location.replace(destination);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Error al iniciar sesión. Verifica tus credenciales.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-bg-glow" aria-hidden="true" />

      <div className="login-card">
        <div className="login-logo">
          <img src="/LogoLigaLight.png" alt="Fundación La Liga — AmaSalvarVidas" />
        </div>

        <div className="login-header">
          <h2>Portal de Accesos</h2>
          <p>Ingresa tus credenciales para continuar</p>
        </div>

        <form onSubmit={handleSubmit} autoComplete="on">
          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              id="username"
              name="username"
              type="text"
              placeholder="Ingresa tu usuario"
              value={form.username}
              onChange={handleChange}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="Ingresa tu contraseña"
              value={form.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
          </div>

          {error && <p className="error-msg">{error}</p>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <span className="btn-loading">
                <span className="spinner" />
                Ingresando...
              </span>
            ) : (
              'Ingresar'
            )}
          </button>
        </form>

        <p className="login-footer">
          Fundación La Liga · <span>AmaSalvarVidas</span>
        </p>
      </div>
    </div>
  );
};

export default Login;
