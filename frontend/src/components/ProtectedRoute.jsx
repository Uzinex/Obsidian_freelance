import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProtectedRoute({ role }) {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user?.profile?.role !== role) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
