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
      { to: '/', label: 'Главная страница' },
      { to: '/about', label: 'О нас' },
    ];

    if (role === 'client') {
      base.push({ to: '/robots', label: 'Роботы' });
    } else {
      base.push({ to: '/orders', label: 'Работы' });
    }

    base.push({ to: '/freelancers', label: 'Фрилансеры' });

    if (isAuthenticated) {
      base.push({ to: '/profile', label: 'Профиль' });
    }

    return base;
  }, [role, isAuthenticated]);

  return (
    <header className="header">
      <Link to="/" className="header-logo">
        <img src="/logo.svg" alt="Obsidian Freelance" />
        <span>OBSIDIAN FREELANCE</span>
      </Link>
      <nav className="nav-links">
        {navigation.map((item) => (
          <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'button secondary active' : 'button secondary')}>
            {item.label}
          </NavLink>
        ))}
        {role === 'client' && isAuthenticated && (
          <NavLink to="/orders/create" className="button primary">
            Создать заказ
          </NavLink>
        )}
        {!isAuthenticated ? (
          <>
            <NavLink to="/login" className="button secondary">
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
      </nav>
    </header>
  );
}
