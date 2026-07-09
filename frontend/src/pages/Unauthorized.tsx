import React from 'react';
import { useNavigate } from 'react-router-dom';
import PortalIcon from '../components/PortalIcon';

const Unauthorized: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="unauthorized-container">
      <div className="unauthorized-card">
        <span className="unauthorized-icon" aria-hidden="true">
          <PortalIcon name="shield-off" size={28} />
        </span>
        <h2>Acceso no autorizado</h2>
        <p>No tiene permisos para acceder a este recurso.</p>
        <button className="btn-primary" onClick={() => navigate('/dashboard')}>
          Volver al inicio
        </button>
      </div>
    </div>
  );
};

export default Unauthorized;
