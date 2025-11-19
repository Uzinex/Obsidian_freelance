import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  login as loginRequest,
  applyAuthToken,
  fetchProfile,
  authenticateWithGoogle,
} from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import GoogleButton from '../components/GoogleButton.jsx';
import { GOOGLE_CLIENT_ID } from '../utils/googleIdentity.js';

export default function LoginPage() {
  const { register, handleSubmit, formState } = useForm({ defaultValues: { remember: true } });
  const navigate = useNavigate();
  const { login } = useAuth();
  const [params] = useSearchParams();
  const [error, setError] = useState('');
  const [googleLoading, setGoogleLoading] = useState(false);
  const googleEnabled = Boolean(GOOGLE_CLIENT_ID);

  async function onSubmit(data) {
    try {
      setError('');
      const result = await loginRequest({ credential: data.credential, password: data.password });
      const accessToken = result.access ?? result.token;
      if (!accessToken) {
        throw new Error('Access token is missing in the login response.');
      }
      applyAuthToken(accessToken);
      let profile;
      try {
        profile = await fetchProfile();
      } catch (profileError) {
        console.warn('Profile not yet completed', profileError);
      }
      login(accessToken, { ...result.user, profile }, data.remember);
      navigate(params.get('next') || '/profile');
    } catch (err) {
      setError('Неверный логин или пароль.');
    }
  }

  async function handleGoogleLogin(credential) {
    if (!credential || googleLoading || !googleEnabled) {
      return;
    }
    setGoogleLoading(true);
    setError('');
    try {
      const result = await authenticateWithGoogle({ credential, action: 'login' });
      if (!result.access) {
        throw new Error('Access token отсутствует.');
      }
      applyAuthToken(result.access);
      let profile;
      try {
        profile = await fetchProfile();
      } catch (profileError) {
        console.warn('Profile not yet completed', profileError);
      }
      login(result.access, { ...result.user, profile }, true);
      navigate(params.get('next') || '/profile');
    } catch (err) {
      const message = err?.response?.data ? collectErrorMessage(err.response.data) : 'Не удалось войти через Google.';
      setError(message);
    } finally {
      setGoogleLoading(false);
    }
  }

  function collectErrorMessage(payload) {
    if (!payload) return 'Не удалось выполнить запрос.';
    if (typeof payload === 'string') return payload;
    if (Array.isArray(payload)) return payload.join(' ');
    return Object.values(payload)
      .map((value) => {
        if (!value) return '';
        if (Array.isArray(value)) return value.join(' ');
        if (typeof value === 'string') return value;
        return JSON.stringify(value);
      })
      .filter(Boolean)
      .join(' ');
  }

  return (
    <div className="card" style={{ maxWidth: '480px', margin: '0 auto' }}>
      <h1>Войти</h1>
      <p>Используйте никнейм или Gmail.</p>
      {googleEnabled && (
        <>
          <div className="google-auth-actions">
            <GoogleButton text="login" onCredential={handleGoogleLogin} disabled={googleLoading} />
            {googleLoading && <p className="muted-text small">Проверяем Google…</p>}
          </div>
          <div className="auth-divider">
            <span>или</span>
          </div>
        </>
      )}
      {error && <div className="alert">{error}</div>}
      <form onSubmit={handleSubmit(onSubmit)}>
        <label htmlFor="credential">Никнейм или Gmail</label>
        <input id="credential" {...register('credential', { required: true })} placeholder="obsidian_master" />

        <label htmlFor="password">Пароль</label>
        <input id="password" type="password" {...register('password', { required: true })} />

        <label className="checkbox" htmlFor="remember" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <input type="checkbox" id="remember" {...register('remember')} /> Запомнить меня
        </label>

        <div className="form-actions">
          <button className="button primary" type="submit" disabled={formState.isSubmitting}>
            Войти
          </button>
        </div>
      </form>
      <div style={{ marginTop: '1.5rem' }}>
        Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link>
      </div>
    </div>
  );
}
