import React from 'react';
import PortalIcon, { type PortalIconName } from './PortalIcon';

export interface StatCard {
  label: string;
  value: string | number;
  hint?: string;
  icon: PortalIconName;
  accent?: 'pink' | 'rose' | 'soft' | 'dark';
}

interface WelcomeBannerProps {
  title: string;
  subtitle: string;
  tagline?: string;
  stats?: StatCard[];
}

const WelcomeBanner: React.FC<WelcomeBannerProps> = ({ title, subtitle, tagline, stats }) => (
  <section className="portal-welcome">
    <div className="portal-welcome-content">
      <p className="portal-welcome-tag">{tagline ?? 'Fundación La Liga · AmaSalvarVidas'}</p>
      <h1 className="portal-welcome-title">{title}</h1>
      <p className="portal-welcome-subtitle">{subtitle}</p>
    </div>
    {stats && stats.length > 0 && (
      <div className="portal-stats-grid">
        {stats.map(stat => (
          <article
            key={stat.label}
            className={`portal-stat-card portal-stat-card--${stat.accent ?? 'pink'}`}
          >
            <span className="portal-stat-icon" aria-hidden="true">
              <PortalIcon name={stat.icon} size={18} />
            </span>
            <div className="portal-stat-body">
              <span className="portal-stat-value" title={String(stat.value)}>
                {stat.value}
              </span>
              <span className="portal-stat-label">{stat.label}</span>
              {stat.hint && (
                <span className="portal-stat-hint" title={stat.hint}>
                  {stat.hint}
                </span>
              )}
            </div>
          </article>
        ))}
      </div>
    )}
  </section>
);

export default WelcomeBanner;
