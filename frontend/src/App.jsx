import { useEffect } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import Header from './components/Header.jsx';
import Footer from './components/Footer.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { useAuth } from './context/AuthContext.jsx';
import { applyAuthToken, fetchProfile } from './api/client.js';
import HomePage from './pages/HomePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import OrdersPage from './pages/OrdersPage.jsx';
import OrderDetailPage from './pages/OrderDetailPage.jsx';
import CreateOrderPage from './pages/CreateOrderPage.jsx';
import FreelancersPage from './pages/FreelancersPage.jsx';
import VerificationPage from './pages/VerificationPage.jsx';
import VerificationRequestsPage from './pages/VerificationRequestsPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import ModerationQueuePage from './pages/ModerationQueuePage.jsx';
import DisputeBackofficePage from './pages/DisputeBackofficePage.jsx';

export default function App() {
  const { token, user, login, isAuthenticated } = useAuth();
  const location = useLocation();

  useEffect(() => {
    applyAuthToken(token);
  }, [token]);

  useEffect(() => {
    async function hydrateProfile() {
      if (!token || !isAuthenticated) return;
      try {
        const profile = await fetchProfile();
        login(token, { ...user, profile });
      } catch (error) {
        console.error('Не удалось получить профиль пользователя', error);
      }
    }
    hydrateProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAuthenticated]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/verification" element={<VerificationPage />} />
          </Route>
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/:orderId" element={<OrderDetailPage />} />
          <Route element={<ProtectedRoute role="client" requireVerified />}>
            <Route path="/orders/create" element={<CreateOrderPage />} />
          </Route>
          <Route element={<ProtectedRoute requireAdmin />}>
            <Route path="/verification/requests" element={<VerificationRequestsPage />} />
          </Route>
          <Route element={<ProtectedRoute requireStaffRole="moderator" />}>
            <Route path="/staff/moderation" element={<ModerationQueuePage />} />
          </Route>
          <Route element={<ProtectedRoute requireStaffRole="finance" />}>
            <Route path="/staff/disputes" element={<DisputeBackofficePage />} />
          </Route>
          <Route path="/freelancers" element={<FreelancersPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
