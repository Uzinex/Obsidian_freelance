import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { logout as logoutRequest, applyAuthToken } from '../api/client.js';

const navItems = [
  { to: '/orders', label: 'Работа' },
  { to: '/freelancers', label: 'Фрилансеры' },
  { to: '/orders/create', label: 'Создать заказ', auth: true, role: 'client' },
  { to: '/profile', label: 'Профиль', auth: true },
];

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

  return (
    <header className="header">
      <Link to="/" className="header-logo">
        <img src="/logo.svg" alt="Obsidian Freelance" />
        <span>OBSIDIAN FREELANCE</span>
      </Link>
      <nav className="nav-links">
        {navItems.map((item) => {
          if (item.auth && !isAuthenticated) return null;
          if (item.role && item.role !== role) return null;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'button secondary' : 'button secondary')}
            >
              {item.label}
            </NavLink>
          );
        })}
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
