import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { login as loginRequest, applyAuthToken, fetchProfile } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function LoginPage() {
  const { register, handleSubmit, formState } = useForm({ defaultValues: { remember: true } });
  const navigate = useNavigate();
  const { login } = useAuth();
  const [params] = useSearchParams();
  const [error, setError] = useState('');

  async function onSubmit(data) {
    try {
      setError('');
      const result = await loginRequest({ credential: data.credential, password: data.password });
      applyAuthToken(result.token);
      let profile;
      try {
        profile = await fetchProfile();
      } catch (profileError) {
        console.warn('Profile not yet completed', profileError);
      }
      login(result.token, { ...result.user, profile }, data.remember);
      navigate(params.get('next') || '/profile');
    } catch (err) {
      setError('Неверный логин или пароль.');
    }
  }

  return (
    <div className="card" style={{ maxWidth: '480px', margin: '0 auto' }}>
      <h1>Войти</h1>
      <p>Используйте никнейм или Gmail.</p>
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
