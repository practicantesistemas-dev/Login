import React, { useMemo, useState } from 'react';
import PortalIcon from './PortalIcon';
import { dedupeApps } from '../utils/portalHelpers';
import type { Application } from '../types';

type EstadoFilter = 'todas' | 'activa' | 'inactiva';

interface AdminAppsCatalogProps {
  applications: Application[];
  updatingUrl: string | null;
  onSetEstado: (url: string, estado: 'activa' | 'inactiva') => void;
}

const AdminAppsCatalog: React.FC<AdminAppsCatalogProps> = ({
  applications,
  updatingUrl,
  onSetEstado,
}) => {
  const [search, setSearch] = useState('');
  const [estadoFilter, setEstadoFilter] = useState<EstadoFilter>('todas');

  const uniqueApps = useMemo(() => dedupeApps(applications), [applications]);

  const filteredApps = useMemo(() => {
    const term = search.trim().toLowerCase();
    return uniqueApps.filter(app => {
      const matchesSearch =
        !term ||
        app.name.toLowerCase().includes(term) ||
        app.url.toLowerCase().includes(term);
      const matchesEstado = estadoFilter === 'todas' || app.estado === estadoFilter;
      return matchesSearch && matchesEstado;
    });
  }, [uniqueApps, search, estadoFilter]);

  const counts = useMemo(
    () => ({
      todas: uniqueApps.length,
      activa: uniqueApps.filter(app => app.estado === 'activa').length,
      inactiva: uniqueApps.filter(app => app.estado === 'inactiva').length,
    }),
    [uniqueApps],
  );

  return (
    <div className="admin-apps-catalog">
      <div className="admin-apps-toolbar">
        <div className="admin-apps-search-row">
          <div className="portal-search-wrap admin-apps-search-wrap">
            <span className="portal-search-icon" aria-hidden="true">
              <PortalIcon name="search" size={16} />
            </span>
            <input
              type="search"
              className="portal-search-input admin-apps-search-input"
              placeholder="Buscar por nombre o URL..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              aria-label="Buscar aplicación en catálogo"
            />
            {search.trim() && (
              <button
                type="button"
                className="admin-apps-search-clear"
                onClick={() => setSearch('')}
                aria-label="Limpiar búsqueda"
              >
                ×
              </button>
            )}
          </div>
        </div>

        <div className="admin-apps-filter-row">
          <span className="admin-apps-filter-label">Estado</span>
          <div className="admin-apps-filter-pills" role="tablist" aria-label="Filtrar catálogo">
            {(
              [
                ['todas', 'Todas', counts.todas],
                ['activa', 'Activas', counts.activa],
                ['inactiva', 'Inactivas', counts.inactiva],
              ] as const
            ).map(([value, label, count]) => (
              <button
                key={value}
                type="button"
                role="tab"
                aria-selected={estadoFilter === value}
                className={`admin-apps-pill ${estadoFilter === value ? 'admin-apps-pill--active' : ''}`}
                onClick={() => setEstadoFilter(value)}
              >
                {label}
                <span className="admin-apps-pill-count">{count}</span>
              </button>
            ))}
          </div>
        </div>

        <p className="admin-apps-result-meta admin-apps-catalog-meta">
          Mostrando {filteredApps.length} de {uniqueApps.length} aplicaciones únicas
        </p>
      </div>

      <div className="admin-apps-catalog-list">
        {filteredApps.length === 0 ? (
          <div className="admin-apps-empty-state">
            <PortalIcon name="search-empty" size={28} />
            <p>No hay aplicaciones que coincidan con la búsqueda.</p>
          </div>
        ) : (
          filteredApps.map(app => {
            const isUpdating = updatingUrl === app.url;
            const isActive = app.estado === 'activa';
            return (
              <article key={`${app.id}-${app.url}`} className="admin-catalog-row">
                <div className="admin-catalog-row-main">
                  <div className="admin-catalog-row-head">
                    <h3 className="admin-catalog-name" title={app.name}>
                      {app.name}
                    </h3>
                    <span className={`admin-app-estado admin-app-estado--${app.estado}`}>
                      {isActive ? 'Activa' : 'Inactiva'}
                    </span>
                  </div>
                  <p className="admin-catalog-url" title={app.url}>
                    {app.url}
                  </p>
                  {(app.linked_count ?? 1) > 1 && (
                    <p className="admin-catalog-linked">
                      {app.linked_count} registros en BD con este enlace
                    </p>
                  )}
                </div>
                <div className="admin-catalog-actions">
                  {isActive ? (
                    <button
                      type="button"
                      className="admin-catalog-btn admin-catalog-btn--inactive"
                      disabled={isUpdating}
                      onClick={() => onSetEstado(app.url, 'inactiva')}
                    >
                      {isUpdating ? 'Guardando...' : 'Desactivar'}
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="admin-catalog-btn admin-catalog-btn--active"
                      disabled={isUpdating}
                      onClick={() => onSetEstado(app.url, 'activa')}
                    >
                      {isUpdating ? 'Guardando...' : 'Activar'}
                    </button>
                  )}
                </div>
              </article>
            );
          })
        )}
      </div>
    </div>
  );
};

export default AdminAppsCatalog;
