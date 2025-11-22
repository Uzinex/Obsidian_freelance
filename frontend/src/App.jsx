import { useEffect } from 'react';
import { Navigate, Outlet, Route, Routes, useLocation, useParams } from 'react-router-dom';
import Header from './components/Header.jsx';
import Footer from './components/Footer.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { useAuth } from './context/AuthContext.jsx';
import { DEFAULT_LOCALE, LocaleProvider, SUPPORTED_LOCALES } from './context/LocaleContext.jsx';
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
import NotificationSettingsPage from './pages/NotificationSettingsPage.jsx';
import CookieConsentBanner from './components/CookieConsentBanner.jsx';
import CategoriesShowcasePage from './pages/public/CategoriesShowcasePage.jsx';
import PublicProfilePage from './pages/public/PublicProfilePage.jsx';
import FAQPage from './pages/public/FAQPage.jsx';
import BlogIndexPage from './pages/public/BlogIndexPage.jsx';
import BlogArticlePage from './pages/public/BlogArticlePage.jsx';
import ContactsPage from './pages/public/ContactsPage.jsx';
import TermsPage from './pages/public/TermsPage.jsx';
import PrivacyPage from './pages/public/PrivacyPage.jsx';
import CookiesPage from './pages/public/CookiesPage.jsx';

function PublicLayout() {
  const { locale } = useParams();
  if (!SUPPORTED_LOCALES.includes(locale)) {
    return <Navigate to={`/${DEFAULT_LOCALE}`} replace />;
  }
  return (
    <LocaleProvider>
      <div className="app-shell">
        <Header />
        <main className="main-content">
          <Outlet />
        </main>
        <Footer />
        <CookieConsentBanner />
      </div>
    </LocaleProvider>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/:locale" element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="contacts" element={<ContactsPage />} />
        <Route path="how-it-works" element={<Navigate to="../about#how-it-works" replace />} />
        <Route path="escrow" element={<Navigate to="../about#escrow" replace />} />
        <Route path="categories" element={<CategoriesShowcasePage />} />
        <Route path="profiles/:slug" element={<PublicProfilePage />} />
        <Route path="faq" element={<FAQPage />} />
        <Route path="blog" element={<BlogIndexPage />} />
        <Route path="blog/:slug" element={<BlogArticlePage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/:orderId" element={<OrderDetailPage />} />
        <Route element={<ProtectedRoute role="client" requireVerified />}>
          <Route path="orders/create" element={<CreateOrderPage />} />
        </Route>
        <Route path="freelancers" element={<FreelancersPage />} />
        <Route element={<ProtectedRoute />}> 
          <Route path="profile" element={<ProfilePage />} />
          <Route path="verification" element={<VerificationPage />} />
          <Route path="settings/notifications" element={<NotificationSettingsPage />} />
        </Route>
        <Route element={<ProtectedRoute requireAdmin />}>
          <Route path="verification/requests" element={<VerificationRequestsPage />} />
        </Route>
        <Route element={<ProtectedRoute requireStaffRole="moderator" />}>
          <Route path="staff/moderation" element={<ModerationQueuePage />} />
        </Route>
        <Route element={<ProtectedRoute requireStaffRole="finance" />}>
          <Route path="staff/disputes" element={<DisputeBackofficePage />} />
        </Route>
        <Route path="terms" element={<TermsPage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="cookies" element={<CookiesPage />} />
        <Route path="pricing" element={<Navigate to="../profile#pricing" replace />} />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/ru" replace />} />
    </Routes>
  );
}

export default function App() {
  const { token, user, login, logout, isAuthenticated } = useAuth();
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
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          console.warn('Сессия больше недействительна, выполняем выход', error);
          applyAuthToken(null);
          logout();
          return;
        }
        console.error('Не удалось получить профиль пользователя', error);
      }
    }
    hydrateProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, isAuthenticated]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return <AppRoutes />;
}
