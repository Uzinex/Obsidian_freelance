import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const AuthContext = createContext(null);

const STORAGE_KEY = 'obsidian_freelance_auth';
const VERIFICATION_ADMIN_EMAIL =
  import.meta.env.VITE_VERIFICATION_ADMIN_EMAIL?.toLowerCase() || 'fdilov1@gmail.com';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setToken(parsed.token);
        setUser(parsed.user);
      } catch (error) {
        console.error('Failed to parse auth state', error);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoading(false);
  }, []);

  const login = (authToken, authUser, rememberMe = true) => {
    setToken(authToken);
    setUser(authUser);
    if (rememberMe) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: authToken, user: authUser }));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const isVerificationAdmin = useMemo(() => {
    return (user?.email || '').toLowerCase() === VERIFICATION_ADMIN_EMAIL;
  }, [user]);

  const staffRoles = user?.profile?.staff_roles || [];
  const isModerator = staffRoles.includes('moderator') || staffRoles.includes('staff');
  const isFinance = staffRoles.includes('finance');

  const value = useMemo(
    () => ({
      token,
      user,
      login,
      logout,
      loading,
      isAuthenticated: Boolean(token),
      isVerificationAdmin,
      staffRoles,
      isModerator,
      isFinance,
    }),
    [token, user, loading, isVerificationAdmin, staffRoles, isModerator, isFinance],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return ctx;
}
