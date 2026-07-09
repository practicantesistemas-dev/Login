import React from 'react';

interface PortalNavbarProps {
  nombres: string;
  roleLabel: string;
  onLogout: () => void;
  children?: React.ReactNode;
}

const PortalNavbar: React.FC<PortalNavbarProps> = ({ nombres, roleLabel, onLogout, children }) => (
  <nav className="navbar portal-navbar">
    <div className="navbar-brand">
      <img src="/LogoLigaLight.png" alt="Fundación La Liga" className="navbar-logo" />
    </div>
    <div className="navbar-info">
      <div className="navbar-user-block">
        <span className="navbar-user">{nombres}</span>
        <span className="navbar-role">{roleLabel}</span>
      </div>
      {children}
      <button type="button" className="btn-logout" onClick={onLogout}>
        Salir
      </button>
    </div>
  </nav>
);

export default PortalNavbar;
