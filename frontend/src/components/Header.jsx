import { useMemo } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import Icon from './Icon.jsx';

export default function Header() {
  const { isAuthenticated } = useAuth();
  const { buildPath } = useLocale();

  const navigation = useMemo(() => {
    const base = [
      {
        to: '/',
        label: 'Главная',
        icon: 'home',
      },
      {
        to: '/about',
        label: 'О нас',
        icon: 'info',
      },
    ];

    base.push({
      to: '/orders',
      label: 'Работы',
      icon: 'orders',
    });

    base.push({
      to: '/freelancers',
      label: 'Фрилансеры',
      icon: 'team',
    });

    if (isAuthenticated) {
      base.push({
        to: '/profile',
        label: 'Профиль',
        icon: 'user',
      });
      base.push({
        to: '/settings/notifications',
        label: 'Уведомления',
        icon: 'bell',
      });
    }

    return base;
  }, [isAuthenticated]);

  return (
    <header className="header">
      <div className="header-inner">
        <Link to={buildPath('/')} className="header-logo">
          <img
            src="/logo.svg"
            alt="Obsidian Freelance"
            loading="lazy"
            decoding="async"
            width="40"
            height="40"
          />
          <div className="header-logo-text">
            <span>OBSIDIAN</span>
            <strong>FREELANCE</strong>
          </div>
        </Link>
        <nav className="nav-links">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={buildPath(item.to)}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              <Icon name={item.icon} size={20} className="nav-icon" decorative />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="header-actions">
          {!isAuthenticated ? (
            <>
              <NavLink to="/login" className="button ghost">
                Войти
              </NavLink>
              <NavLink to="/register" className="button primary">
                Регистрация
              </NavLink>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
