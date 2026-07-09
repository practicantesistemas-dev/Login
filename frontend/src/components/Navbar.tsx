import React from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/authService';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const username = localStorage.getItem('username') ?? 'Usuario';
  const role     = localStorage.getItem('role') ?? '';

  const handleLogout = (): void => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">Portal de Accesos</div>
      <div className="navbar-info">
        <span className="navbar-user">{username}</span>
        <span className="navbar-role">{role}</span>
        <button className="btn-logout" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </div>
    </nav>
  );
};

export default Navbar;