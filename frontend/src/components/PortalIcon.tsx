import React from 'react';

export type PortalIconName =
  | 'apps'
  | 'building'
  | 'user'
  | 'shield'
  | 'settings'
  | 'users'
  | 'check'
  | 'globe'
  | 'layers'
  | 'search'
  | 'inbox'
  | 'search-empty'
  | 'lock'
  | 'chevron-right'
  | 'shield-off';

interface PortalIconProps {
  name: PortalIconName;
  className?: string;
  size?: number;
}

const PortalIcon: React.FC<PortalIconProps> = ({ name, className = '', size = 20 }) => {
  const props = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    xmlns: 'http://www.w3.org/2000/svg',
    className: `portal-icon ${className}`.trim(),
    'aria-hidden': true as const,
  };

  switch (name) {
    case 'apps':
      return (
        <svg {...props}>
          <rect x="3" y="3" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
          <rect x="13" y="3" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
          <rect x="3" y="13" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
          <rect x="13" y="13" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.75" />
        </svg>
      );
    case 'building':
      return (
        <svg {...props}>
          <path d="M4 21V7l8-4 8 4v14" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M4 21h16M9 21v-6h6v6" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M9 9h.01M12 9h.01M15 9h.01" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      );
    case 'user':
      return (
        <svg {...props}>
          <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.75" />
          <path d="M5 20c0-3.314 3.134-6 7-6s7 2.686 7 6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'shield':
      return (
        <svg {...props}>
          <path d="M12 3l7 3v6c0 4.418-3.015 7.942-7 9-3.985-1.058-7-4.582-7-9V6l7-3z" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'settings':
      return (
        <svg {...props}>
          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.75" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'users':
      return (
        <svg {...props}>
          <circle cx="9" cy="8" r="3" stroke="currentColor" strokeWidth="1.75" />
          <path d="M2 20c0-3.314 2.686-6 7-6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
          <circle cx="17" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.75" />
          <path d="M14 20c0-2.761 1.79-5 5-5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'check':
      return (
        <svg {...props}>
          <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
          <path d="M8 12l2.5 2.5L16 9" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'globe':
      return (
        <svg {...props}>
          <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
          <path d="M3 12h18M12 3c2.5 2.667 4 5.667 4 9s-1.5 6.333-4 9c-2.5-2.667-4-5.667-4-9s1.5-6.333 4-9z" stroke="currentColor" strokeWidth="1.75" />
        </svg>
      );
    case 'layers':
      return (
        <svg {...props}>
          <path d="M12 3l9 5-9 5-9-5 9-5z" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M3 12l9 5 9-5M3 17l9 5 9-5" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
        </svg>
      );
    case 'search':
      return (
        <svg {...props}>
          <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.75" />
          <path d="M16 16l4.5 4.5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'inbox':
      return (
        <svg {...props}>
          <path d="M4 4h16v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M4 13h5l1.5 3h3L15 13h5" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
        </svg>
      );
    case 'search-empty':
      return (
        <svg {...props}>
          <circle cx="10.5" cy="10.5" r="5.5" stroke="currentColor" strokeWidth="1.75" />
          <path d="M15 15l4 4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
          <path d="M8 10.5h5" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'lock':
      return (
        <svg {...props}>
          <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.75" />
          <path d="M8 11V8a4 4 0 118 0v3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    case 'chevron-right':
      return (
        <svg {...props}>
          <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'shield-off':
      return (
        <svg {...props}>
          <path d="M12 3l7 3v6c0 2.2-.9 4.2-2.4 5.7" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M5 21c3.985-1.058 7-4.582 7-9V6" stroke="currentColor" strokeWidth="1.75" strokeLinejoin="round" />
          <path d="M3 3l18 18" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        </svg>
      );
    default:
      return null;
  }
};

export default PortalIcon;
