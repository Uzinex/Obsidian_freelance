import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { registerUser, applyAuthToken } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [errorMessage, setErrorMessage] = useState('');

  async function onSubmit(data) {
    try {
      setErrorMessage('');
      clearErrors();
      const result = await registerUser(data);
      applyAuthToken(result.token);
      const userPayload = result.user ?? result;
      login(result.token, userPayload, true);
      navigate('/profile');
    } catch (err) {
      const responseData = err.response?.data;
      if (responseData && typeof responseData === 'object' && !Array.isArray(responseData)) {
        const collectedMessages = [];
        Object.entries(responseData).forEach(([field, messages]) => {
          const normalizedMessages = Array.isArray(messages) ? messages.join(' ') : String(messages);
          if (field !== 'non_field_errors') {
            setError(field, { type: 'server', message: normalizedMessages });
          }
          if (normalizedMessages) {
            collectedMessages.push(normalizedMessages);
          }
        });
        setErrorMessage(collectedMessages.join(' ') || 'Не удалось зарегистрироваться. Проверьте данные.');
      } else if (typeof responseData === 'string') {
        setErrorMessage(responseData);
      } else {
        setErrorMessage('Не удалось зарегистрироваться. Проверьте данные.');
      }
    }
  }

  return (
    <div className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
      <h1>Создать аккаунт</h1>
      <p>После регистрации обязательно заполните профиль.</p>
      {errorMessage && <div className="alert">{errorMessage}</div>}
      <form onSubmit={handleSubmit(onSubmit)} className="grid two">
        <div>
          <label htmlFor="last_name">Фамилия</label>
          <input id="last_name" {...register('last_name', { required: 'Укажите фамилию' })} />
          {errors.last_name && <p className="error-text">{errors.last_name.message}</p>}
        </div>
        <div>
          <label htmlFor="first_name">Имя</label>
          <input id="first_name" {...register('first_name', { required: 'Укажите имя' })} />
          {errors.first_name && <p className="error-text">{errors.first_name.message}</p>}
        </div>
        <div>
          <label htmlFor="patronymic">Отчество</label>
          <input id="patronymic" {...register('patronymic')} />
        </div>
        <div>
          <label htmlFor="nickname">Никнейм</label>
          <input id="nickname" {...register('nickname', { required: 'Укажите никнейм' })} placeholder="obsidian_master" />
          {errors.nickname && <p className="error-text">{errors.nickname.message}</p>}
        </div>
        <div>
          <label htmlFor="email">Gmail</label>
          <input id="email" type="email" {...register('email', { required: 'Укажите Gmail' })} placeholder="you@gmail.com" />
          {errors.email && <p className="error-text">{errors.email.message}</p>}
        </div>
        <div>
          <label htmlFor="birth_year">Год рождения</label>
          <input id="birth_year" type="number" min="1900" {...register('birth_year', { required: 'Укажите год рождения' })} />
          {errors.birth_year && <p className="error-text">{errors.birth_year.message}</p>}
        </div>
        <div>
          <label htmlFor="password">Пароль</label>
          <input id="password" type="password" {...register('password', { required: 'Укажите пароль' })} />
          {errors.password && <p className="error-text">{errors.password.message}</p>}
        </div>
        <div>
          <label htmlFor="password_confirm">Повторите пароль</label>
          <input id="password_confirm" type="password" {...register('password_confirm', { required: 'Повторите пароль' })} />
          {errors.password_confirm && <p className="error-text">{errors.password_confirm.message}</p>}
        </div>
        <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
          <button className="button primary" type="submit" disabled={isSubmitting}>
            Зарегистрироваться
          </button>
        </div>
      </form>
    </div>
  );
}
