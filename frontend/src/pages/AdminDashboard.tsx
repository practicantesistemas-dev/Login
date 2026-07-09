import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PortalNavbar from '../components/PortalNavbar';
import WelcomeBanner from '../components/WelcomeBanner';
import PortalIcon from '../components/PortalIcon';
import AdminAppsPicker from '../components/AdminAppsPicker';
import AdminAppsCatalog from '../components/AdminAppsCatalog';
import {
  createManagedUser,
  deactivateManagedUser,
  getApplications,
  getDepartments,
  getManagedUsers,
  setApplicationEstado,
  updateManagedUser,
} from '../services/adminService';
import { getPortalRole, isAdminRole, logout } from '../services/authService';
import { getGreeting, getRoleLabel, ROLE_LABELS, dedupeApps } from '../utils/portalHelpers';
import type {
  Application,
  Department,
  ManagedUser,
  UserCreatePayload,
  UserUpdatePayload,
} from '../types';

interface AdminDashboardProps {
  onLogout: () => void;
}

type FormMode = 'create' | 'edit';

const DEFAULT_REPORT_TIPOS = ['user', 'root'];

const EMPTY_FORM: UserCreatePayload = {
  username: '',
  password: '',
  nombres: '',
  num_id: '',
  id_area: 0,
  report_tipo: 'user',
  email_personal: '',
  email_laboral: '',
  portal_role: 'usuario',
  app_ids: [],
};

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const portalRole = getPortalRole();
  const isGlobalAdmin = portalRole === 'admin';
  const areaName = localStorage.getItem('area_name') ?? '';
  const nombres = localStorage.getItem('nombres') ?? 'Administrador';
  const firstName = nombres.split(' ')[0];
  const roleLabel = getRoleLabel(portalRole);

  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [reportTipos, setReportTipos] = useState<string[]>(DEFAULT_REPORT_TIPOS);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState<number | ''>('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState<FormMode>('create');
  const [form, setForm] = useState<UserCreatePayload>(EMPTY_FORM);
  const [editingUsername, setEditingUsername] = useState<string | null>(null);
  const [appFilter, setAppFilter] = useState('');
  const [appEstadoFilter, setAppEstadoFilter] = useState<'todas' | 'activa' | 'inactiva'>('todas');
  const [updatingAppUrl, setUpdatingAppUrl] = useState<string | null>(null);
  const [catalogMessage, setCatalogMessage] = useState<string | null>(null);
  const [showAppsCatalog, setShowAppsCatalog] = useState(false);

  const lockedAreaId = useMemo(() => {
    const raw = localStorage.getItem('id_area');
    return raw ? Number(raw) : null;
  }, []);

  const loadData = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const filters = {
        ...(departmentFilter !== '' ? { id_area: departmentFilter } : {}),
        ...(debouncedSearch.trim() ? { q: debouncedSearch.trim() } : {}),
      };
      const [usersData, deptData, appsData] = await Promise.all([
        getManagedUsers(filters),
        getDepartments(),
        getApplications(),
      ]);
      setUsers(usersData);
      setDepartments(deptData);
      setApplications(dedupeApps(appsData));
      setReportTipos(DEFAULT_REPORT_TIPOS);
    } catch {
      setError('No se pudo cargar la información de administración.');
    } finally {
      setLoading(false);
    }
  }, [departmentFilter, debouncedSearch]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearch(search);
    }, 350);
    return () => window.clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    if (!isAdminRole()) {
      navigate('/dashboard', { replace: true });
      return;
    }
    void loadData();
  }, [loadData, navigate]);

  useEffect(() => {
    if (!isGlobalAdmin && lockedAreaId != null) {
      setDepartmentFilter(lockedAreaId);
    }
  }, [isGlobalAdmin, lockedAreaId]);

  const activeUsers = users.filter(u => u.active).length;
  const activeAppsCount = applications.filter(app => app.estado === 'activa').length;
  const inactiveAppsCount = applications.length - activeAppsCount;

  const filteredAppIds = useMemo(() => {
    const term = appFilter.trim().toLowerCase();
    return applications
      .filter(app => {
        const matchesSearch =
          !term ||
          app.name.toLowerCase().includes(term) ||
          app.url.toLowerCase().includes(term);
        const matchesEstado = appEstadoFilter === 'todas' || app.estado === appEstadoFilter;
        return matchesSearch && matchesEstado;
      })
      .map(app => app.id);
  }, [applications, appFilter, appEstadoFilter]);

  const selectVisibleApps = (): void => {
    setForm(prev => {
      const merged = new Set([...(prev.app_ids ?? []), ...filteredAppIds]);
      return { ...prev, app_ids: [...merged] };
    });
  };

  const deselectVisibleApps = (): void => {
    const visibleSet = new Set(filteredAppIds);
    setForm(prev => ({
      ...prev,
      app_ids: (prev.app_ids ?? []).filter(id => !visibleSet.has(id)),
    }));
  };

  const adminSubtitle = isGlobalAdmin
    ? 'Gestione usuarios, roles y permisos de todas las áreas de la fundación.'
    : `Administre colaboradores y permisos del departamento ${areaName || 'asignado'}.`;

  const openCreateForm = (): void => {
    setFormMode('create');
    setEditingUsername(null);
    const defaultArea =
      departmentFilter !== ''
        ? departmentFilter
        : isGlobalAdmin
          ? (departments[0]?.id ?? 0)
          : (lockedAreaId ?? 0);
    setForm({
      ...EMPTY_FORM,
      id_area: defaultArea,
      report_tipo: reportTipos[0] ?? 'user',
      portal_role: 'usuario',
      app_ids: [],
    });
    setAppFilter('');
    setShowForm(true);
  };

  const openEditForm = (user: ManagedUser): void => {
    setFormMode('edit');
    setEditingUsername(user.username);
    setAppFilter('');
    setForm({
      username: user.username,
      password: '',
      nombres: user.nombres,
      num_id: user.num_id,
      id_area: user.id_area ?? 0,
      report_tipo: user.report_tipo || reportTipos[0] || 'user',
      email_personal: user.email_personal,
      email_laboral: user.email_laboral,
      portal_role: user.portal_role,
      app_ids: user.app_ids,
    });
    setShowForm(true);
  };

  const toggleApp = (appId: number): void => {
    setForm(prev => {
      const exists = prev.app_ids?.includes(appId);
      const nextIds = exists
        ? (prev.app_ids ?? []).filter(id => id !== appId)
        : [...(prev.app_ids ?? []), appId];
      return { ...prev, app_ids: nextIds };
    });
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      if (formMode === 'create') {
        await createManagedUser({
          ...form,
          report_tipo: form.report_tipo?.trim() || 'user',
        });
      } else if (editingUsername) {
        const payload: UserUpdatePayload = {
          nombres: form.nombres,
          num_id: form.num_id,
          id_area: form.id_area,
          report_tipo: form.report_tipo,
          email_personal: form.email_personal,
          email_laboral: form.email_laboral,
          portal_role: form.portal_role,
          app_ids: form.app_ids,
        };
        if (form.password) {
          payload.password = form.password;
        }
        await updateManagedUser(editingUsername, payload);
      }
      setShowForm(false);
      await loadData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo guardar el usuario.';
      setError(typeof message === 'string' ? message : 'No se pudo guardar el usuario.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivate = async (username: string): Promise<void> => {
    if (!window.confirm(`¿Desactivar al usuario ${username}?`)) return;
    setError(null);
    try {
      await deactivateManagedUser(username);
      await loadData();
    } catch {
      setError('No se pudo desactivar el usuario.');
    }
  };

  const handleLogout = async (): Promise<void> => {
    await logout();
    onLogout();
    navigate('/login', { replace: true });
  };

  const handleSetAppEstado = async (
    url: string,
    estado: 'activa' | 'inactiva',
  ): Promise<void> => {
    const verb = estado === 'activa' ? 'activar' : 'desactivar';
    if (
      !window.confirm(
        `¿Confirma ${verb} esta aplicación? Se actualizarán todos los registros con el mismo enlace en la base de datos.`,
      )
    ) {
      return;
    }

    setUpdatingAppUrl(url);
    setError(null);
    setCatalogMessage(null);
    try {
      const result = await setApplicationEstado(url, estado);
      setCatalogMessage(
        `"${result.name}" ${estado === 'activa' ? 'activada' : 'desactivada'} en ${result.updated_count} registro(s).`,
      );
      await loadData();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo actualizar el estado de la aplicación.';
      setError(typeof message === 'string' ? message : 'No se pudo actualizar el estado de la aplicación.');
    } finally {
      setUpdatingAppUrl(null);
    }
  };

  return (
    <div className="dashboard-layout portal-layout">
      <PortalNavbar
        nombres={nombres}
        roleLabel={areaName ? `${roleLabel} · ${areaName}` : roleLabel}
        onLogout={() => void handleLogout()}
      >
        <button type="button" className="btn-nav-action" onClick={() => navigate('/dashboard')}>
          Mis aplicaciones
        </button>
      </PortalNavbar>

      <div className="portal-main admin-container">
        <WelcomeBanner
          tagline="Panel de administración"
          title={`${getGreeting()}, ${firstName}`}
          subtitle={adminSubtitle}
          stats={[
            {
              icon: 'users',
              value: loading ? '…' : users.length,
              label: 'Usuarios',
              hint: `${activeUsers} activos`,
              accent: 'pink',
            },
            {
              icon: 'check',
              value: loading ? '…' : activeUsers,
              label: 'Activos',
              hint: 'Con acceso al portal',
              accent: 'rose',
            },
            {
              icon: 'globe',
              value: loading ? '…' : activeAppsCount,
              label: 'Apps activas',
              hint: `${inactiveAppsCount} inactivas`,
              accent: 'soft',
            },
            {
              icon: 'layers',
              value: isGlobalAdmin ? departments.length : 1,
              label: isGlobalAdmin ? 'Departamentos' : 'Área',
              hint: isGlobalAdmin ? 'Áreas registradas' : areaName || 'Departamento',
              accent: 'dark',
            },
          ]}
        />

        <section className="portal-section">
          <div className="portal-section-header admin-section-header">
            <div>
              <h2 className="portal-section-title">Usuarios del portal</h2>
              <p className="portal-section-desc">
                Cree cuentas, asigne permisos y mantenga actualizada la información de cada colaborador.
              </p>
            </div>
            <button type="button" className="btn-primary btn-primary--inline" onClick={openCreateForm}>
              + Nuevo usuario
            </button>
          </div>

          {error && <p className="error-msg portal-error">{error}</p>}

          <div className="admin-toolbar-card">
            <div className="admin-toolbar">
              <div className="portal-search-wrap portal-search-wrap--toolbar">
                <span className="portal-search-icon" aria-hidden="true">
                  <PortalIcon name="search" size={16} />
                </span>
                <input
                  type="search"
                  className="portal-search-input"
                  placeholder="Buscar por nombre o usuario..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              {isGlobalAdmin ? (
                <select
                  className="admin-input admin-select admin-dept-filter"
                  value={departmentFilter}
                  onChange={e => {
                    const value = e.target.value;
                    setDepartmentFilter(value === '' ? '' : Number(value));
                  }}
                >
                  <option value="">Todos los departamentos</option>
                  {departments.map(dept => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="admin-dept-badge">{areaName || 'Mi departamento'}</span>
              )}
              <button
                type="button"
                className="btn-secondary admin-apps-catalog-btn"
                onClick={() => setShowAppsCatalog(true)}
              >
                Gestionar aplicaciones
              </button>
              <span className="admin-result-count">
                {loading ? 'Cargando...' : `${users.length} usuario(s) encontrado(s)`}
              </span>
            </div>
          </div>

          {loading ? (
            <div className="loading-container portal-loading">
              <span className="spinner" />
              Cargando usuarios...
            </div>
          ) : users.length === 0 ? (
            <div className="portal-empty-state">
              <span className="portal-empty-icon" aria-hidden="true">
                <PortalIcon name="user" size={32} />
              </span>
              <h3>No hay usuarios</h3>
              <p>No se encontraron usuarios con los criterios indicados. Ajuste la búsqueda o registre uno nuevo.</p>
              <button type="button" className="btn-primary btn-primary--inline" onClick={openCreateForm}>
                Crear primer usuario
              </button>
            </div>
          ) : (
            <div className="users-grid-4">
              {users.map(user => (
                <article
                  key={user.id_usuario ?? `${user.username}-${user.num_id}`}
                  className={`user-card ${!user.active ? 'user-card--inactive' : ''}`}
                >
                  <div className="user-card-top">
                    <div className="user-card-avatar" aria-hidden="true">
                      {user.nombres.charAt(0).toUpperCase()}
                    </div>
                    <div className="user-card-meta">
                      <h3 className="user-card-name" title={user.nombres}>
                        {user.nombres}
                      </h3>
                      <span className="user-card-username" title={user.username}>
                        @{user.username}
                      </span>
                    </div>
                    <span
                      className={`user-card-status ${user.active ? 'user-card-status--active' : 'user-card-status--inactive'}`}
                    >
                      {user.active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>

                  <dl className="user-card-details">
                    <div className="user-card-detail">
                      <dt>Departamento</dt>
                      <dd title={user.area_name || undefined}>{user.area_name || '—'}</dd>
                    </div>
                    <div className="user-card-detail">
                      <dt>Rol</dt>
                      <dd title={ROLE_LABELS[user.portal_role] ?? user.portal_role}>
                        {ROLE_LABELS[user.portal_role] ?? user.portal_role}
                      </dd>
                    </div>
                    <div className="user-card-detail">
                      <dt>Aplicaciones</dt>
                      <dd>{user.app_ids.length} asignada(s)</dd>
                    </div>
                    <div className="user-card-detail">
                      <dt>Cédula</dt>
                      <dd title={user.num_id}>{user.num_id}</dd>
                    </div>
                  </dl>

                  <div className="user-card-actions">
                    <button type="button" className="user-card-btn" onClick={() => openEditForm(user)}>
                      Editar
                    </button>
                    {user.active && (
                      <button
                        type="button"
                        className="user-card-btn user-card-btn--danger"
                        onClick={() => void handleDeactivate(user.username)}
                      >
                        Desactivar
                      </button>
                    )}
                  </div>
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

      {showForm && (
        <div className="admin-modal-backdrop" onClick={() => setShowForm(false)}>
          <div className="admin-modal admin-modal--wide" onClick={e => e.stopPropagation()}>
            <div className="admin-modal-header">
              <div>
                <h2>{formMode === 'create' ? 'Nuevo usuario' : 'Editar usuario'}</h2>
                {formMode === 'edit' && editingUsername && (
                  <p className="admin-modal-subtitle">@{editingUsername}</p>
                )}
              </div>
              <button type="button" className="admin-modal-close" onClick={() => setShowForm(false)}>
                ×
              </button>
            </div>

            <form className="admin-form" onSubmit={e => void handleSubmit(e)}>
              <section className="admin-form-section">
                <h3 className="admin-section-title">Acceso</h3>
                <div className="admin-form-grid">
                  <div className="admin-field">
                    <label htmlFor="username">Usuario</label>
                    <input
                      id="username"
                      className="admin-input"
                      value={form.username}
                      onChange={e => setForm(prev => ({ ...prev, username: e.target.value }))}
                      disabled={formMode === 'edit'}
                      required
                    />
                  </div>

                  <div className="admin-field">
                    <label htmlFor="password">
                      {formMode === 'create' ? 'Contraseña' : 'Nueva contraseña (opcional)'}
                    </label>
                    <input
                      id="password"
                      className="admin-input"
                      type="password"
                      maxLength={20}
                      value={form.password}
                      onChange={e => setForm(prev => ({ ...prev, password: e.target.value }))}
                      required={formMode === 'create'}
                      placeholder={formMode === 'edit' ? 'Dejar vacío para no cambiar' : 'Máx. 20 caracteres'}
                    />
                  </div>

                  <div className="admin-field">
                    <label htmlFor="report_tipo">Tipo en reportes (SSO)</label>
                    <select
                      id="report_tipo"
                      className="admin-input admin-select"
                      value={form.report_tipo}
                      onChange={e => setForm(prev => ({ ...prev, report_tipo: e.target.value }))}
                      required
                    >
                      {reportTipos.map(tipo => (
                        <option key={tipo} value={tipo}>
                          {tipo}
                        </option>
                      ))}
                    </select>
                    <span className="admin-field-hint">
                      Obligatorio para acceso a aplicaciones legacy ({reportTipos.join(', ')})
                    </span>
                  </div>
                </div>
              </section>

              <section className="admin-form-section">
                <h3 className="admin-section-title">Datos personales</h3>
                <div className="admin-form-grid">
                  <div className="admin-field admin-field-full">
                    <label htmlFor="nombres">Nombres completos</label>
                    <input
                      id="nombres"
                      className="admin-input"
                      value={form.nombres}
                      onChange={e => setForm(prev => ({ ...prev, nombres: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="admin-field">
                    <label htmlFor="num_id">Cédula / NUM_ID</label>
                    <input
                      id="num_id"
                      className="admin-input"
                      value={form.num_id}
                      onChange={e => setForm(prev => ({ ...prev, num_id: e.target.value }))}
                      required
                    />
                  </div>

                  <div className="admin-field">
                    <label htmlFor="email_laboral">Email laboral</label>
                    <input
                      id="email_laboral"
                      className="admin-input"
                      type="email"
                      value={form.email_laboral}
                      onChange={e => setForm(prev => ({ ...prev, email_laboral: e.target.value }))}
                    />
                  </div>

                  <div className="admin-field admin-field-full">
                    <label htmlFor="email_personal">Email personal</label>
                    <input
                      id="email_personal"
                      className="admin-input"
                      type="email"
                      value={form.email_personal}
                      onChange={e => setForm(prev => ({ ...prev, email_personal: e.target.value }))}
                    />
                  </div>
                </div>
              </section>

              <section className="admin-form-section">
                <h3 className="admin-section-title">Departamento y permisos</h3>
                <div className="admin-form-grid">
                  <div className="admin-field">
                    <label htmlFor="id_area">Departamento</label>
                    <select
                      id="id_area"
                      className="admin-input admin-select"
                      value={form.id_area}
                      onChange={e => setForm(prev => ({ ...prev, id_area: Number(e.target.value) }))}
                      disabled={!isGlobalAdmin}
                      required
                    >
                      {departments.map(dept => (
                        <option key={dept.id} value={dept.id}>
                          {dept.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="admin-field">
                    <label htmlFor="portal_role">Rol en el portal</label>
                    <select
                      id="portal_role"
                      className="admin-input admin-select"
                      value={form.portal_role}
                      onChange={e => setForm(prev => ({ ...prev, portal_role: e.target.value }))}
                      disabled={!isGlobalAdmin}
                    >
                      <option value="usuario">Usuario normal</option>
                      {isGlobalAdmin && <option value="area_admin">Administrador de área</option>}
                      {isGlobalAdmin && <option value="admin">Administrador global</option>}
                    </select>
                  </div>
                </div>
              </section>

              <AdminAppsPicker
                applications={applications}
                selectedIds={form.app_ids ?? []}
                search={appFilter}
                estadoFilter={appEstadoFilter}
                onSearchChange={setAppFilter}
                onEstadoFilterChange={setAppEstadoFilter}
                onToggleApp={toggleApp}
                onSelectVisible={selectVisibleApps}
                onDeselectVisible={deselectVisibleApps}
              />

              <div className="admin-form-actions">
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary btn-primary--inline" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar cambios'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAppsCatalog && (
        <div
          className="admin-modal-backdrop"
          onClick={() => {
            setShowAppsCatalog(false);
            setCatalogMessage(null);
          }}
        >
          <div
            className="admin-modal admin-modal--wide admin-modal--catalog"
            onClick={e => e.stopPropagation()}
          >
            <div className="admin-modal-header">
              <div>
                <h2>Catálogo de aplicaciones</h2>
                <p className="admin-modal-subtitle">
                  Active o desactive por enlace. El cambio aplica a todos los registros con la misma URL.
                </p>
              </div>
              <button
                type="button"
                className="admin-modal-close"
                onClick={() => {
                  setShowAppsCatalog(false);
                  setCatalogMessage(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="admin-modal-body">
              {catalogMessage && <p className="admin-success-msg">{catalogMessage}</p>}
              <AdminAppsCatalog
                applications={applications}
                updatingUrl={updatingAppUrl}
                onSetEstado={(url, estado) => void handleSetAppEstado(url, estado)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
