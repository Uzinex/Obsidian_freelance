import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { useLocale } from '../context/LocaleContext.jsx';

export default function ProtectedRoute({ role, requireVerified = false, requireAdmin = false, requireStaffRole }) {
  const { isAuthenticated, loading, user, isVerificationAdmin, staffRoles } = useAuth();
  const { buildPath } = useLocale();

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (role && user?.profile?.role !== role) {
    return <Navigate to={buildPath('/')} replace />;
  }

  if (requireAdmin && !isVerificationAdmin) {
    return <Navigate to={buildPath('/')} replace />;
  }

  if (requireStaffRole) {
    const hasStaffRole = staffRoles?.includes(requireStaffRole) || staffRoles?.includes('staff');
    if (!hasStaffRole) {
      return <Navigate to={buildPath('/')} replace />;
    }
  }

  if (requireVerified && !user?.profile?.is_verified) {
    return <Navigate to={buildPath('/verification')} replace />;
  }

  return <Outlet />;
}
