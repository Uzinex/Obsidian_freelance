import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProtectedRoute({ role, requireVerified = false, requireAdmin = false, requireStaffRole }) {
  const { isAuthenticated, loading, user, isVerificationAdmin, staffRoles } = useAuth();

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user?.profile?.role !== role) {
    return <Navigate to="/" replace />;
  }

  if (requireAdmin && !isVerificationAdmin) {
    return <Navigate to="/" replace />;
  }

  if (requireStaffRole) {
    const hasStaffRole = staffRoles?.includes(requireStaffRole) || staffRoles?.includes('staff');
    if (!hasStaffRole) {
      return <Navigate to="/" replace />;
    }
  }

  if (requireVerified && !user?.profile?.is_verified) {
    return <Navigate to="/verification" replace />;
  }

  return <Outlet />;
}
