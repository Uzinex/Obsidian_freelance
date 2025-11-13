import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { registerUser, applyAuthToken } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function RegisterPage() {
  const { register, handleSubmit, formState } = useForm();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState('');

  async function onSubmit(data) {
    try {
      setError('');
      const result = await registerUser(data);
      applyAuthToken(result.token);
      login(result.token, result.user, true);
      navigate('/profile');
    } catch (err) {
      setError('Не удалось зарегистрироваться. Проверьте данные.');
    }
  }

  return (
    <div className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
      <h1>Создать аккаунт</h1>
      <p>После регистрации обязательно заполните профиль.</p>
      {error && <div className="alert">{error}</div>}
      <form onSubmit={handleSubmit(onSubmit)} className="grid two">
        <div>
          <label htmlFor="last_name">Фамилия</label>
          <input id="last_name" {...register('last_name', { required: true })} />
        </div>
        <div>
          <label htmlFor="first_name">Имя</label>
          <input id="first_name" {...register('first_name', { required: true })} />
        </div>
        <div>
          <label htmlFor="patronymic">Отчество</label>
          <input id="patronymic" {...register('patronymic')} />
        </div>
        <div>
          <label htmlFor="nickname">Никнейм</label>
          <input id="nickname" {...register('nickname', { required: true })} placeholder="obsidian_master" />
        </div>
        <div>
          <label htmlFor="email">Gmail</label>
          <input id="email" type="email" {...register('email', { required: true })} placeholder="you@gmail.com" />
        </div>
        <div>
          <label htmlFor="birth_year">Год рождения</label>
          <input id="birth_year" type="number" min="1900" {...register('birth_year', { required: true })} />
        </div>
        <div>
          <label htmlFor="password">Пароль</label>
          <input id="password" type="password" {...register('password', { required: true })} />
        </div>
        <div>
          <label htmlFor="password_confirm">Повторите пароль</label>
          <input id="password_confirm" type="password" {...register('password_confirm', { required: true })} />
        </div>
        <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
          <button className="button primary" type="submit" disabled={formState.isSubmitting}>
            Зарегистрироваться
          </button>
        </div>
      </form>
    </div>
  );
}
