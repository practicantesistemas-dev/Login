import React, { useMemo } from 'react';
import PortalIcon from './PortalIcon';
import { dedupeApps } from '../utils/portalHelpers';
import type { Application } from '../types';

type EstadoFilter = 'todas' | 'activa' | 'inactiva';

interface AdminAppsPickerProps {
  applications: Application[];
  selectedIds: number[];
  search: string;
  estadoFilter: EstadoFilter;
  onSearchChange: (value: string) => void;
  onEstadoFilterChange: (value: EstadoFilter) => void;
  onToggleApp: (appId: number) => void;
  onSelectVisible: () => void;
  onDeselectVisible: () => void;
}

function highlightMatch(text: string, term: string): React.ReactNode {
  const query = term.trim();
  if (!query) return text;

  const lowerText = text.toLowerCase();
  const lowerQuery = query.toLowerCase();
  const index = lowerText.indexOf(lowerQuery);
  if (index === -1) return text;

  return (
    <>
      {text.slice(0, index)}
      <mark className="admin-app-highlight">{text.slice(index, index + query.length)}</mark>
      {text.slice(index + query.length)}
    </>
  );
}

const AdminAppsPicker: React.FC<AdminAppsPickerProps> = ({
  applications,
  selectedIds,
  search,
  estadoFilter,
  onSearchChange,
  onEstadoFilterChange,
  onToggleApp,
  onSelectVisible,
  onDeselectVisible,
}) => {
  const uniqueApplications = useMemo(() => dedupeApps(applications), [applications]);

  const counts = useMemo(
    () => ({
      todas: uniqueApplications.length,
      activa: uniqueApplications.filter(app => app.estado === 'activa').length,
      inactiva: uniqueApplications.filter(app => app.estado === 'inactiva').length,
    }),
    [uniqueApplications],
  );

  const filteredApps = useMemo(() => {
    const term = search.trim().toLowerCase();
    return uniqueApplications.filter(app => {
      const matchesSearch =
        !term ||
        app.name.toLowerCase().includes(term) ||
        app.url.toLowerCase().includes(term);
      const matchesEstado = estadoFilter === 'todas' || app.estado === estadoFilter;
      return matchesSearch && matchesEstado;
    });
  }, [uniqueApplications, search, estadoFilter]);

  const visibleSelectedCount = filteredApps.filter(app => selectedIds.includes(app.id)).length;
  const hasSearch = search.trim().length > 0;

  return (
    <section className="admin-apps-picker">
      <div className="admin-apps-picker-head">
        <div>
          <h3 className="admin-section-title">Aplicaciones permitidas</h3>
          <p className="admin-section-hint">
            {selectedIds.length} seleccionada(s) en total · {counts.activa} activa(s) ·{' '}
            {counts.inactiva} inactiva(s)
          </p>
        </div>
      </div>

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
              onChange={e => onSearchChange(e.target.value)}
              aria-label="Buscar aplicación"
            />
            {hasSearch && (
              <button
                type="button"
                className="admin-apps-search-clear"
                onClick={() => onSearchChange('')}
                aria-label="Limpiar búsqueda"
              >
                ×
              </button>
            )}
          </div>
        </div>

        <div className="admin-apps-filter-row">
          <span className="admin-apps-filter-label">Estado</span>
          <div className="admin-apps-filter-pills" role="tablist" aria-label="Filtrar por estado">
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
                onClick={() => onEstadoFilterChange(value)}
              >
                {label}
                <span className="admin-apps-pill-count">{count}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="admin-apps-actions-row">
          <span className="admin-apps-result-meta">
            Mostrando {filteredApps.length} de {uniqueApplications.length}
            {hasSearch || estadoFilter !== 'todas'
              ? ` · ${visibleSelectedCount} visible(s) seleccionada(s)`
              : ''}
          </span>
          <div className="admin-apps-bulk-actions">
            <button
              type="button"
              className="admin-apps-bulk-btn"
              onClick={onSelectVisible}
              disabled={filteredApps.length === 0}
            >
              Seleccionar visibles
            </button>
            <button
              type="button"
              className="admin-apps-bulk-btn"
              onClick={onDeselectVisible}
              disabled={visibleSelectedCount === 0}
            >
              Quitar visibles
            </button>
          </div>
        </div>
      </div>

      <div className="admin-apps-list" role="list">
        {filteredApps.length === 0 ? (
          <div className="admin-apps-empty-state">
            <PortalIcon name="search-empty" size={28} />
            <p>No hay aplicaciones que coincidan con la búsqueda o el filtro.</p>
            {(hasSearch || estadoFilter !== 'todas') && (
              <button
                type="button"
                className="admin-apps-bulk-btn"
                onClick={() => {
                  onSearchChange('');
                  onEstadoFilterChange('todas');
                }}
              >
                Restablecer filtros
              </button>
            )}
          </div>
        ) : (
          filteredApps.map(app => {
            const isSelected = selectedIds.includes(app.id);
            return (
              <label
                key={app.id}
                role="listitem"
                className={`admin-app-row ${isSelected ? 'admin-app-row--selected' : ''} ${
                  app.estado === 'activa' ? 'admin-app-row--active-url' : 'admin-app-row--inactive-url'
                }`}
              >
                <input
                  type="checkbox"
                  className="admin-app-row-check"
                  checked={isSelected}
                  onChange={() => onToggleApp(app.id)}
                />
                <span className="admin-app-row-body">
                  <span className="admin-app-row-top">
                    <span className="admin-app-item-name" title={app.name}>
                      {highlightMatch(app.name, search)}
                    </span>
                    <span
                      className={`admin-app-estado admin-app-estado--${app.estado}`}
                    >
                      {app.estado === 'activa' ? 'Activa' : 'Inactiva'}
                    </span>
                  </span>
                  <span className="admin-app-row-url" title={app.url}>
                    {highlightMatch(app.url, search)}
                  </span>
                </span>
              </label>
            );
          })
        )}
      </div>
    </section>
  );
};

export default AdminAppsPicker;
