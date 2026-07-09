import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PortalNavbar from '../components/PortalNavbar';
import WelcomeBanner from '../components/WelcomeBanner';
import PortalIcon from '../components/PortalIcon';
import { launchApp, logout, isAdminRole, getPortalRole } from '../services/authService';
import { getPages } from '../services/pagesService';
import { getAppGradient, getAppInitial, getGreeting, getRoleLabel, dedupeApps } from '../utils/portalHelpers';
import type { PageLink } from '../types';

interface DashboardProps {
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const [pages, setPages] = useState<PageLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openingId, setOpeningId] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const nombres = localStorage.getItem('nombres') ?? localStorage.getItem('username') ?? 'Usuario';
  const firstName = nombres.split(' ')[0];
  const portalRole = getPortalRole();
  const roleLabel = getRoleLabel(portalRole);
  const areaName = localStorage.getItem('area_name') ?? '';
  const isAdmin = isAdminRole();

  useEffect(() => {
    const fetchPages = async (): Promise<void> => {
      try {
        const data = await getPages();
        setPages(dedupeApps(data));
      } catch (err: unknown) {
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 401) return;
        setError('No se pudieron cargar las aplicaciones disponibles.');
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, []);

  const filteredPages = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return pages;
    return pages.filter(
      page =>
        page.name.toLowerCase().includes(term) ||
        page.ip.toLowerCase().includes(term) ||
        page.url.toLowerCase().includes(term),
    );
  }, [pages, search]);

  const handleLogout = async (): Promise<void> => {
    await logout();
    onLogout();
    navigate('/login', { replace: true });
  };

  const handleAccess = async (page: PageLink): Promise<void> => {
    setOpeningId(page.id);
    setError(null);
    try {
      await launchApp(page.url);
    } catch (err: unknown) {
      const response = (err as { response?: { status?: number; data?: { detail?: string } } })
        ?.response;
      const status = response?.status;
      if (status === 401) return;
      const detail = response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'No se pudo abrir la aplicación. Intente de nuevo o contacte al administrador.',
      );
    } finally {
      setOpeningId(null);
    }
  };

  const welcomeSubtitle = isAdmin
    ? 'Acceda a sus sistemas autorizados. Desde este portal también puede administrar usuarios y permisos.'
    : 'Seleccione una aplicación para ingresar de forma segura. Solo se muestran los sistemas autorizados para su perfil.';

  const sharedProjects = [
    {
      id: 'sistemassalud',
      name: 'Sistema Salud',
      description: 'Módulo de salud compartido con la misma cuenta del portal.',
      url: '/sistemassalud/',
    },
    {
      id: 'tesoreri',
      name: 'Tesorería',
      description: 'Acceso directo al módulo de tesorería con la cuenta del portal.',
      url: '/tesoreri/',
    },
  ];

  const handleOpenSharedProject = (url: string): void => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="dashboard-layout portal-layout">
      <PortalNavbar nombres={nombres} roleLabel={roleLabel} onLogout={() => void handleLogout()}>
        {isAdmin && (
          <button type="button" className="btn-nav-action" onClick={() => navigate('/admin')}>
            Administración
          </button>
        )}
      </PortalNavbar>

      <div className="portal-main">
        <WelcomeBanner
          tagline="Portal de Accesos"
          title={`${getGreeting()}, ${firstName}`}
          subtitle={welcomeSubtitle}
          stats={[
            {
              icon: 'apps',
              value: loading ? '…' : pages.length,
              label: 'Aplicaciones',
              hint: 'Disponibles para usted',
              accent: 'pink',
            },
            {
              icon: 'building',
              value: areaName || '—',
              label: 'Área',
              hint: 'Departamento asignado',
              accent: 'rose',
            },
            {
              icon: 'user',
              value: roleLabel,
              label: 'Rol',
              hint: 'En el portal',
              accent: 'soft',
            },
            {
              icon: isAdmin ? 'settings' : 'shield',
              value: isAdmin ? 'Admin' : 'Verificada',
              label: isAdmin ? 'Administración' : 'Sesión',
              hint: isAdmin ? 'Gestión de usuarios' : 'Acceso autenticado',
              accent: 'dark',
            },
          ]}
        />

        <section className="portal-section">
          <div style={{ marginBottom: '1.25rem' }}>
            <h2 className="portal-section-title">Acceso a otros proyectos</h2>
            <p className="portal-section-desc">
              Ingrese a los proyectos internos desde este mismo portal usando las mismas credenciales.
            </p>
          </div>

          <div className="apps-grid-4" style={{ marginBottom: '1.5rem' }}>
            {sharedProjects.map(project => (
              <article key={project.id} className="app-card">
                <div className="app-card-body">
                  <h3 className="app-card-name">{project.name}</h3>
                  <p className="app-card-desc">{project.description}</p>
                </div>
                <button
                  type="button"
                  className="app-card-btn"
                  onClick={() => handleOpenSharedProject(project.url)}
                >
                  Abrir
                  <PortalIcon name="chevron-right" size={16} className="app-card-btn-icon" />
                </button>
              </article>
            ))}
          </div>

          <div className="portal-section-header">
            <div>
              <h2 className="portal-section-title">Aplicaciones autorizadas</h2>
              <p className="portal-section-desc">
                Seleccione <strong>Ingresar</strong> para abrir cada sistema con su sesión del portal.
              </p>
            </div>
            {!loading && pages.length > 0 && (
              <div className="portal-search-wrap">
                <span className="portal-search-icon" aria-hidden="true">
                  <PortalIcon name="search" size={16} />
                </span>
                <input
                  type="search"
                  className="portal-search-input"
                  placeholder="Buscar aplicación..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  aria-label="Buscar aplicación"
                />
              </div>
            )}
          </div>

          {loading && (
            <div className="loading-container portal-loading">
              <span className="spinner" />
              Cargando tus aplicaciones...
            </div>
          )}

          {error && <p className="error-msg portal-error">{error}</p>}

          {!loading && !error && pages.length === 0 && (
            <div className="portal-empty-state">
              <span className="portal-empty-icon" aria-hidden="true">
                <PortalIcon name="inbox" size={32} />
              </span>
              <h3>Sin aplicaciones asignadas</h3>
              <p>
                No tiene sistemas disponibles en este momento. Si considera que se trata de un error,
                contacte al administrador de su área.
              </p>
            </div>
          )}

          {!loading && pages.length > 0 && filteredPages.length === 0 && (
            <div className="portal-empty-state portal-empty-state--compact">
              <span className="portal-empty-icon" aria-hidden="true">
                <PortalIcon name="search-empty" size={28} />
              </span>
              <h3>Sin resultados</h3>
              <p>Intente con otro criterio de búsqueda.</p>
            </div>
          )}

          {!loading && filteredPages.length > 0 && (
            <div className="apps-grid-4">
              {filteredPages.map(page => (
                <article key={page.id} className="app-card">
                  <div
                    className="app-card-icon"
                    style={{ background: getAppGradient(page.name) }}
                    aria-hidden="true"
                  >
                    {getAppInitial(page.name)}
                  </div>
                  <div className="app-card-body">
                    <h3 className="app-card-name">{page.name}</h3>
                    {page.description && (
                      <p className="app-card-desc">{page.description}</p>
                    )}
                    {page.url && (
                      <span className="app-card-url" title={page.url}>
                        {page.url}
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    className="app-card-btn"
                    onClick={() => void handleAccess(page)}
                    disabled={openingId === page.id}
                  >
                    {openingId === page.id ? (
                      <span className="btn-loading">
                        <span className="spinner spinner--white" />
                        Abriendo...
                      </span>
                    ) : (
                      <>
                        Ingresar
                        <PortalIcon name="chevron-right" size={16} className="app-card-btn-icon" />
                      </>
                    )}
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>

        <footer className="portal-footer">
          <p>
            Fundación La Liga ·{' '}
            <span className="portal-footer-accent">AmaSalvarVidas</span>
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Dashboard;
