import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import AdminAppsPicker from './AdminAppsPicker';
import { getMe, isAdminRole, updateMyProfile } from '../services/authService';
import { getApplications } from '../services/adminService';
import type { Application, ProfileUpdatePayload, UserInfo } from '../types';

interface ProfileFormState {
  nombres: string;
  email_personal: string;
  email_laboral: string;
  password: string;
  confirmPassword: string;
  app_ids: number[];
}

interface UserProfileButtonProps {
  onSaved?: (profile: UserInfo) => void;
}

const EMPTY_FORM: ProfileFormState = {
  nombres: '',
  email_personal: '',
  email_laboral: '',
  password: '',
  confirmPassword: '',
  app_ids: [],
};

const UserProfileButton: React.FC<UserProfileButtonProps> = ({ onSaved }) => {
  const [open, setOpen] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingApps, setLoadingApps] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<UserInfo | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [appSearch, setAppSearch] = useState('');
  const [appEstadoFilter, setAppEstadoFilter] = useState<'todas' | 'activa' | 'inactiva'>('todas');
  const [form, setForm] = useState<ProfileFormState>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const canManageApps = isAdminRole();

  const openProfile = async (): Promise<void> => {
    setOpen(true);
    setLoadingProfile(true);
    setLoadingApps(canManageApps);
    setError(null);

    try {
      const [data, apps] = await Promise.all([
        getMe(),
        canManageApps ? getApplications() : Promise.resolve([]),
      ]);
      setProfile(data);
      setApplications(apps);
      setForm({
        nombres: data.nombres ?? '',
        email_personal: data.email_personal ?? '',
        email_laboral: data.email_laboral ?? '',
        password: '',
        confirmPassword: '',
        app_ids: data.app_ids ?? [],
      });
    } catch {
      setError('No se pudo cargar su perfil.');
    } finally {
      setLoadingProfile(false);
      setLoadingApps(false);
    }
  };

  const closeProfile = (): void => {
    setOpen(false);
    setError(null);
    setSaving(false);
    setLoadingProfile(false);
  };

  const handleSave = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const nombres = form.nombres.trim();
    const emailPersonal = form.email_personal.trim();
    const emailLaboral = form.email_laboral.trim();
    const newPassword = form.password.trim();

    if (!nombres) {
      setError('El nombre es obligatorio.');
      setSaving(false);
      return;
    }

    if (newPassword && newPassword !== form.confirmPassword.trim()) {
      setError('Las contraseñas no coinciden.');
      setSaving(false);
      return;
    }

    const payload: ProfileUpdatePayload = {
      nombres,
      email_personal: emailPersonal,
      email_laboral: emailLaboral,
    };
    if (newPassword) {
      payload.password = newPassword;
    }
    if (canManageApps) {
      payload.app_ids = form.app_ids;
    }

    try {
      const updated = await updateMyProfile(payload);
      localStorage.setItem('nombres', updated.nombres);
      if (updated.email_personal) {
        localStorage.setItem('email_personal', updated.email_personal);
      } else {
        localStorage.removeItem('email_personal');
      }
      if (updated.email_laboral) {
        localStorage.setItem('email_laboral', updated.email_laboral);
      } else {
        localStorage.removeItem('email_laboral');
      }
      if (updated.area_name) {
        localStorage.setItem('area_name', updated.area_name);
      }
      onSaved?.(updated);
      closeProfile();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'No se pudo actualizar su perfil.';
      setError(typeof message === 'string' ? message : 'No se pudo actualizar su perfil.');
    } finally {
      setSaving(false);
    }
  };

  const modal = open ? (
    <div className="admin-modal-backdrop" onClick={closeProfile}>
      <div className="admin-modal admin-modal--wide" onClick={e => e.stopPropagation()}>
            <div className="admin-modal-header">
              <div>
                <h2>Mi perfil</h2>
                <p className="admin-modal-subtitle">
                  Actualice sus datos personales y contraseña sin afectar el panel de administración.
                </p>
              </div>
              <button type="button" className="admin-modal-close" onClick={closeProfile}>
                ×
              </button>
            </div>

            {loadingProfile ? (
              <div className="loading-container portal-loading">
                <span className="spinner" />
                Cargando perfil...
              </div>
            ) : (
              <form className="admin-form" onSubmit={handleSave}>
                {error && <p className="error-msg portal-error">{error}</p>}

                <section className="admin-form-section">
                  <h3 className="admin-section-title">Datos de cuenta</h3>
                  <div className="admin-form-grid">
                    <div className="admin-field">
                      <label htmlFor="profile-username">Usuario</label>
                      <input
                        id="profile-username"
                        className="admin-input"
                        value={profile?.username ?? ''}
                        readOnly
                      />
                    </div>
                    <div className="admin-field">
                      <label htmlFor="profile-role">Rol</label>
                      <input
                        id="profile-role"
                        className="admin-input"
                        value={profile?.portal_role ?? profile?.role ?? ''}
                        readOnly
                      />
                    </div>
                    <div className="admin-field">
                      <label htmlFor="profile-num-id">Cédula</label>
                      <input id="profile-num-id" className="admin-input" value={profile?.num_id ?? ''} readOnly />
                    </div>
                    <div className="admin-field">
                      <label htmlFor="profile-area">Área</label>
                      <input id="profile-area" className="admin-input" value={profile?.area_name ?? ''} readOnly />
                    </div>
                  </div>
                </section>

                <section className="admin-form-section">
                  <h3 className="admin-section-title">Datos personales</h3>
                  <div className="admin-form-grid">
                    <div className="admin-field admin-field-full">
                      <label htmlFor="profile-nombres">Nombres completos</label>
                      <input
                        id="profile-nombres"
                        className="admin-input"
                        value={form.nombres}
                        onChange={e => setForm(prev => ({ ...prev, nombres: e.target.value }))}
                        required
                      />
                    </div>

                    <div className="admin-field">
                      <label htmlFor="profile-email-personal">Email personal</label>
                      <input
                        id="profile-email-personal"
                        className="admin-input"
                        type="email"
                        value={form.email_personal}
                        onChange={e => setForm(prev => ({ ...prev, email_personal: e.target.value }))}
                      />
                    </div>

                    <div className="admin-field">
                      <label htmlFor="profile-email-laboral">Email laboral</label>
                      <input
                        id="profile-email-laboral"
                        className="admin-input"
                        type="email"
                        value={form.email_laboral}
                        onChange={e => setForm(prev => ({ ...prev, email_laboral: e.target.value }))}
                      />
                    </div>
                  </div>
                </section>

                <section className="admin-form-section">
                  <h3 className="admin-section-title">Seguridad</h3>
                  <div className="admin-form-grid">
                    <div className="admin-field">
                      <label htmlFor="profile-password">Nueva contraseña</label>
                      <input
                        id="profile-password"
                        className="admin-input"
                        type="password"
                        maxLength={20}
                        value={form.password}
                        onChange={e => setForm(prev => ({ ...prev, password: e.target.value }))}
                        placeholder="Dejar vacío para no cambiar"
                      />
                    </div>
                    <div className="admin-field">
                      <label htmlFor="profile-confirm-password">Confirmar contraseña</label>
                      <input
                        id="profile-confirm-password"
                        className="admin-input"
                        type="password"
                        maxLength={20}
                        value={form.confirmPassword}
                        onChange={e => setForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                        placeholder="Repita la nueva contraseña"
                      />
                    </div>
                  </div>
                </section>

                {canManageApps && (
                  <section className="admin-form-section">
                    <h3 className="admin-section-title">Aplicaciones permitidas</h3>
                    {loadingApps ? (
                      <div className="loading-container portal-loading">
                        <span className="spinner" />
                        Cargando aplicaciones...
                      </div>
                    ) : (
                      <AdminAppsPicker
                        applications={applications}
                        selectedIds={form.app_ids}
                        search={appSearch}
                        estadoFilter={appEstadoFilter}
                        onSearchChange={setAppSearch}
                        onEstadoFilterChange={setAppEstadoFilter}
                        onToggleApp={appId =>
                          setForm(prev => {
                            const exists = prev.app_ids.includes(appId);
                            return {
                              ...prev,
                              app_ids: exists
                                ? prev.app_ids.filter(id => id !== appId)
                                : [...prev.app_ids, appId],
                            };
                          })
                        }
                        onSelectVisible={() => {
                          const term = appSearch.trim().toLowerCase();
                          const visibleIds = applications
                            .filter(app => {
                              const matchesSearch =
                                !term ||
                                app.name.toLowerCase().includes(term) ||
                                app.url.toLowerCase().includes(term);
                              const matchesEstado =
                                appEstadoFilter === 'todas' || app.estado === appEstadoFilter;
                              return matchesSearch && matchesEstado;
                            })
                            .map(app => app.id);
                          setForm(prev => ({
                            ...prev,
                            app_ids: [...new Set([...prev.app_ids, ...visibleIds])],
                          }));
                        }}
                        onDeselectVisible={() => {
                          const term = appSearch.trim().toLowerCase();
                          const visibleIds = new Set(
                            applications
                              .filter(app => {
                                const matchesSearch =
                                  !term ||
                                  app.name.toLowerCase().includes(term) ||
                                  app.url.toLowerCase().includes(term);
                                const matchesEstado =
                                  appEstadoFilter === 'todas' || app.estado === appEstadoFilter;
                                return matchesSearch && matchesEstado;
                              })
                              .map(app => app.id),
                          );
                          setForm(prev => ({
                            ...prev,
                            app_ids: prev.app_ids.filter(id => !visibleIds.has(id)),
                          }));
                        }}
                      />
                    )}
                  </section>
                )}

                <div className="admin-form-actions">
                  <button type="button" className="btn-secondary" onClick={closeProfile}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn-primary" disabled={saving}>
                    {saving ? 'Guardando...' : 'Actualizar perfil'}
                  </button>
                </div>
              </form>
            )}
      </div>
    </div>
  ) : null;

  return (
    <>
      <button type="button" className="btn-secondary" onClick={() => void openProfile()}>
        Mi perfil
      </button>

      {modal && typeof document !== 'undefined' ? createPortal(modal, document.body) : modal}
    </>
  );
};

export default UserProfileButton;
