import { useMemo } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Header() {
  const { isAuthenticated } = useAuth();

  const navigation = useMemo(() => {
    const base = [
      {
        to: '/',
        label: 'Главная',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/home.png',
      },
      {
        to: '/about',
        label: 'О нас',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/info.png',
      },
    ];

    base.push({
      to: '/orders',
      label: 'Работы',
      icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/task.png',
    });

    base.push({
      to: '/freelancers',
      label: 'Фрилансеры',
      icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/conference-call.png',
    });

    if (isAuthenticated) {
      base.push({
        to: '/profile',
        label: 'Профиль',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/user-male-circle.png',
      });
      base.push({
        to: '/settings/notifications',
        label: 'Уведомления',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/appointment-reminders.png',
      });
    }

    return base;
  }, [isAuthenticated]);

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="header-logo">
          <img src="/logo.svg" alt="Obsidian Freelance" />
          <div className="header-logo-text">
            <span>OBSIDIAN</span>
            <strong>FREELANCE</strong>
          </div>
        </Link>
        <nav className="nav-links">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              <img src={item.icon} alt="" aria-hidden="true" className="nav-icon" />
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
