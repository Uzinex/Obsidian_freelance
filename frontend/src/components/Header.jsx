import { useMemo } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { logout as logoutRequest, applyAuthToken } from '../api/client.js';

export default function Header() {
  const { isAuthenticated, user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logoutRequest();
    } catch (error) {
      console.warn('Failed to logout from API', error);
    }
    applyAuthToken(null);
    logout();
  };

  const role = user?.profile?.role || user?.role;

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

    if (role === 'client') {
      base.push({
        to: '/robots',
        label: 'Работы',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/task.png',
      });
    } else {
      base.push({
        to: '/orders',
        label: 'Работы',
        icon: 'https://img.icons8.com/ios-filled/24/1f1f1f/task.png',
      });
    }

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
    }

    return base;
  }, [role, isAuthenticated]);

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
          ) : (
            <button type="button" className="button primary" onClick={handleLogout}>
              Выйти
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
