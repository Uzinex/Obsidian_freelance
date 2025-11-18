import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  applyAuthToken,
  checkNicknameAvailability,
  fetchProfile,
  resendRegistrationCode,
  startRegistration,
  verifyRegistration,
} from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { DEFAULT_LOCALE, SUPPORTED_LOCALES } from '../context/LocaleContext.jsx';
import { useRecaptcha } from '../utils/useRecaptcha.js';

const MAX_ATTEMPTS = 5;
const PASSWORD_REQUIREMENTS = [
  {
    label: 'Не менее 10 символов',
    validate: (value) => value.length >= 10,
  },
  {
    label: 'Строчные и заглавные буквы',
    validate: (value) => /[a-zа-яё]/.test(value) && /[A-ZА-ЯЁ]/.test(value),
  },
  {
    label: 'Хотя бы одна цифра',
    validate: (value) => /\d/.test(value),
  },
  {
    label: 'Минимум один символ !@#$%^&*',
    validate: (value) => /[!@#$%^&*()_+=\-{}\[\]:;"'`~<>?,./]/.test(value),
  },
];

const STEP_ORDER = ['form', 'code', 'success'];

function maskEmail(email) {
  if (!email) return '';
  const [local, domain] = email.split('@');
  if (!domain) return email;
  const visible = local.slice(0, 2);
  const masked = `${visible}${'*'.repeat(Math.max(local.length - 2, 3))}`;
  return `${masked}@${domain}`;
}

function collectErrorMessage(payload) {
  if (!payload) return 'Не удалось отправить запрос. Попробуйте ещё раз.';
  if (typeof payload === 'string') return payload;
  if (Array.isArray(payload)) return payload.join(' ');
  if (typeof payload === 'object') {
    return Object.values(payload)
      .map((value) => {
        if (!value) return '';
        if (Array.isArray(value)) {
          return value.join(' ');
        }
        if (typeof value === 'string') {
          return value;
        }
        return JSON.stringify(value);
      })
      .filter(Boolean)
      .join(' ');
  }
  return 'Не удалось отправить запрос. Попробуйте ещё раз.';
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { execute: executeRecaptcha, ready: recaptchaReady, isEnabled: isRecaptchaEnabled } = useRecaptcha();
  const [step, setStep] = useState('form');
  const [pendingEmail, setPendingEmail] = useState('');
  const [globalMessage, setGlobalMessage] = useState('');
  const [formError, setFormError] = useState('');
  const [codeError, setCodeError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [resendLoading, setResendLoading] = useState(false);
  const [attemptsLeft, setAttemptsLeft] = useState(MAX_ATTEMPTS);
  const [nicknameStatus, setNicknameStatus] = useState({ state: 'idle', message: '' });

  const {
    register,
    handleSubmit,
    watch,
    setError,
    clearErrors,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    defaultValues: {
      locale: DEFAULT_LOCALE,
      terms_accepted: false,
    },
  });

  const {
    register: registerCode,
    handleSubmit: handleSubmitCode,
    setError: setCodeFieldError,
    reset: resetCodeForm,
    formState: { errors: codeErrors, isSubmitting: isVerifying },
  } = useForm({
    defaultValues: { code: '', auto_login: true },
  });

  const passwordValue = watch('password') || '';
  const passwordConfirm = watch('password_confirm') || '';
  const nicknameValue = watch('nickname') || '';

  const passwordChecks = useMemo(() => {
    return PASSWORD_REQUIREMENTS.map((requirement) => ({
      label: requirement.label,
      valid: requirement.validate(passwordValue),
    }));
  }, [passwordValue]);

  useEffect(() => {
    if (!passwordConfirm) {
      return;
    }
    if (passwordValue !== passwordConfirm) {
      setError('password_confirm', { type: 'manual', message: 'Пароли не совпадают.' });
    } else {
      clearErrors('password_confirm');
    }
  }, [passwordConfirm, passwordValue, setError, clearErrors]);

  useEffect(() => {
    if (!nicknameValue || nicknameValue.trim().length < 3) {
      setNicknameStatus({ state: 'idle', message: '' });
      return undefined;
    }
    const trimmed = nicknameValue.trim();
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setNicknameStatus({ state: 'checking', message: 'Проверяем ник…' });
      try {
        const result = await checkNicknameAvailability(trimmed, { signal: controller.signal });
        if (result.available) {
          setNicknameStatus({ state: 'available', message: result.detail || 'Ник свободен.' });
          clearErrors('nickname');
        } else {
          setNicknameStatus({ state: 'taken', message: result.detail || 'Ник уже используется.' });
          setError('nickname', { type: 'server', message: result.detail || 'Ник уже используется.' });
        }
      } catch (error) {
        if (error?.name === 'CanceledError') {
          return;
        }
        const message = collectErrorMessage(error?.response?.data) || 'Не удалось проверить ник.';
        setNicknameStatus({ state: 'error', message });
      }
    }, 400);
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [nicknameValue, setError]);

  useEffect(() => {
    if (!cooldown) {
      return undefined;
    }
    const interval = setInterval(() => {
      setCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [cooldown]);

  const stepIndex = STEP_ORDER.indexOf(step);

  async function requestCaptchaToken(action) {
    if (!isRecaptchaEnabled) {
      setFormError('reCAPTCHA не настроена. Обратитесь к администратору.');
      throw new Error('Recaptcha disabled');
    }
    if (!recaptchaReady) {
      setFormError('reCAPTCHA ещё загружается. Попробуйте через пару секунд.');
      throw new Error('Recaptcha not ready');
    }
    try {
      const token = await executeRecaptcha(action);
      if (!token) {
        throw new Error('Empty token');
      }
      return token;
    } catch (error) {
      const reason = error?.message || 'Не удалось подтвердить reCAPTCHA.';
      setFormError(reason);
      throw error;
    }
  }

  async function onSubmit(values) {
    setFormError('');
    setGlobalMessage('');
    try {
      const captchaToken = await requestCaptchaToken('register_start');
      const birthYear = values.birth_year ? Number(values.birth_year) : undefined;
      const payload = {
        first_name: values.first_name?.trim(),
        last_name: values.last_name?.trim(),
        patronymic: values.patronymic?.trim() || '',
        nickname: values.nickname?.trim(),
        email: values.email?.trim().toLowerCase(),
        birth_year: birthYear,
        password: values.password,
        password_confirm: undefined,
        locale: values.locale || DEFAULT_LOCALE,
        terms_accepted: values.terms_accepted,
        captcha: captchaToken,
      };
      delete payload.password_confirm;
      const response = await startRegistration(payload);
      setPendingEmail(payload.email);
      setStep('code');
      setGlobalMessage(response.detail);
      setCooldown(response.cooldown ?? 60);
      setAttemptsLeft(MAX_ATTEMPTS);
      resetCodeForm({ code: '', auto_login: true });
    } catch (error) {
      const data = error?.response?.data;
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        Object.entries(data).forEach(([field, message]) => {
          if (field === 'detail' || field === 'non_field_errors') {
            return;
          }
          setError(field, {
            type: 'server',
            message: Array.isArray(message) ? message.join(' ') : String(message),
          });
        });
      }
      setFormError(collectErrorMessage(data));
    }
  }

  async function handleVerify(values) {
    setCodeError('');
    try {
      const response = await verifyRegistration({
        email: pendingEmail,
        code: values.code.trim(),
        auto_login: values.auto_login,
      });
      setSuccessMessage(response.detail);
      if (!response.auto_login) {
        setStep('success');
        return;
      }
      const token = response.access;
      if (token) {
        applyAuthToken(token);
        let profile;
        try {
          profile = await fetchProfile();
        } catch (profileError) {
          console.warn('Не удалось загрузить профиль после регистрации', profileError);
        }
        login(token, { ...response.user, profile }, true);
        navigate('/profile');
      } else {
        setStep('success');
      }
    } catch (error) {
      const data = error?.response?.data;
      const message = collectErrorMessage(data);
      setCodeError(message);
      if (data?.code) {
        setAttemptsLeft((prev) => (prev > 0 ? prev - 1 : 0));
        setCodeFieldError('code', {
          type: 'server',
          message: Array.isArray(data.code) ? data.code.join(' ') : String(data.code),
        });
      }
      if (data?.detail) {
        setFormError(data.detail);
      }
    }
  }

  async function handleResend() {
    if (cooldown > 0 || resendLoading) {
      return;
    }
    setResendLoading(true);
    setFormError('');
    try {
      const captchaToken = await requestCaptchaToken('register_resend');
      const response = await resendRegistrationCode({ email: pendingEmail, captcha: captchaToken });
      setGlobalMessage(response.detail);
      setCooldown(response.cooldown ?? 60);
    } catch (error) {
      const message = collectErrorMessage(error?.response?.data);
      setFormError(message);
    } finally {
      setResendLoading(false);
    }
  }

  function resetFlow() {
    setStep('form');
    setPendingEmail('');
    setGlobalMessage('');
    setCodeError('');
    setFormError('');
    setSuccessMessage('');
    setAttemptsLeft(MAX_ATTEMPTS);
    setNicknameStatus({ state: 'idle', message: '' });
    reset();
    resetCodeForm({ code: '', auto_login: true });
  }

  const maskedEmail = useMemo(() => maskEmail(pendingEmail), [pendingEmail]);

  return (
    <div className="card register-card">
      <div className="stepper" role="list">
        {STEP_ORDER.map((stepName, index) => {
          const isActive = index === stepIndex;
          const isComplete = index < stepIndex;
          const label =
            stepName === 'form' ? 'Данные' : stepName === 'code' ? 'Подтверждение' : 'Готово';
          return (
            <div key={stepName} className={`step ${isActive ? 'is-active' : ''} ${isComplete ? 'is-complete' : ''}`}>
              <div className="step-index">{index + 1}</div>
              <div>
                <div className="step-label">{label}</div>
                <div className="step-caption">
                  {stepName === 'form'
                    ? 'Имя, Gmail, пароль'
                    : stepName === 'code'
                      ? 'Код из письма'
                      : 'Создание аккаунта'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {step === 'form' && (
        <>
          <h1>Создать аккаунт</h1>
          <p className="muted-text">Заполните данные и подтвердите e-mail в течение 10 минут.</p>
          {formError && <div className="alert">{formError}</div>}
          {!isRecaptchaEnabled && (
            <div className="alert">reCAPTCHA не сконфигурирована. Регистрация временно недоступна.</div>
          )}
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
              <input
                id="nickname"
                {...register('nickname', { required: 'Укажите никнейм' })}
                placeholder="obsidian_master"
              />
              {nicknameStatus.state !== 'idle' && (
                <p className={`hint ${nicknameStatus.state}`}>
                  {nicknameStatus.message}
                </p>
              )}
              {errors.nickname && <p className="error-text">{errors.nickname.message}</p>}
            </div>
            <div>
              <label htmlFor="email">Gmail</label>
              <input
                id="email"
                type="email"
                {...register('email', {
                  required: 'Укажите Gmail',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@gmail\.com$/i,
                    message: 'Используйте адрес @gmail.com',
                  },
                })}
                placeholder="you@gmail.com"
              />
              {errors.email && <p className="error-text">{errors.email.message}</p>}
            </div>
            <div>
              <label htmlFor="birth_year">Год рождения</label>
              <input
                id="birth_year"
                type="number"
                min="1900"
                max={new Date().getFullYear()}
                {...register('birth_year', { required: 'Укажите год рождения' })}
              />
              {errors.birth_year && <p className="error-text">{errors.birth_year.message}</p>}
            </div>
            <div>
              <label htmlFor="password">Пароль</label>
              <input
                id="password"
                type="password"
                {...register('password', { required: 'Укажите пароль' })}
              />
            </div>
            <div>
              <label htmlFor="password_confirm">Повторите пароль</label>
              <input
                id="password_confirm"
                type="password"
                {...register('password_confirm', { required: 'Повторите пароль' })}
              />
              {errors.password_confirm && <p className="error-text">{errors.password_confirm.message}</p>}
            </div>
            <div className="password-hints" style={{ gridColumn: '1 / -1' }}>
              <p className="muted-text">Пароль должен соответствовать всем пунктам:</p>
              <ul>
                {passwordChecks.map((check) => (
                  <li key={check.label} className={check.valid ? 'valid' : ''}>
                    {check.valid ? '✅' : '⬜️'} {check.label}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <label htmlFor="locale">Язык писем</label>
              <select id="locale" {...register('locale')}>
                {SUPPORTED_LOCALES.map((loc) => (
                  <option key={loc} value={loc}>
                    {loc === 'ru' ? 'Русский' : "O'zbekcha"}
                  </option>
                ))}
              </select>
            </div>
            <div className="terms-box">
              <label className="checkbox" htmlFor="terms_accepted">
                <input
                  type="checkbox"
                  id="terms_accepted"
                  {...register('terms_accepted', { required: 'Нужно согласиться с условиями' })}
                />
                <span>
                  Я принимаю{' '}
                  <a href={`/${DEFAULT_LOCALE}/terms`} target="_blank" rel="noreferrer">
                    Условия сервиса
                  </a>{' '}
                  и{' '}
                  <a href={`/${DEFAULT_LOCALE}/privacy`} target="_blank" rel="noreferrer">
                    Политику конфиденциальности
                  </a>
                </span>
              </label>
              {errors.terms_accepted && <p className="error-text">{errors.terms_accepted.message}</p>}
            </div>
            <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
              <button className="button primary" type="submit" disabled={isSubmitting || !isRecaptchaEnabled}>
                {isSubmitting ? 'Отправляем…' : 'Продолжить'}
              </button>
            </div>
          </form>
          <p className="recaptcha-note">Форма защищена Google reCAPTCHA (v3).</p>
        </>
      )}

      {step === 'code' && (
        <>
          <h1>Подтвердите e-mail</h1>
          <p>
            Введите 6-значный код из письма, отправленного на <strong>{maskedEmail}</strong>. Он действует 10 минут.
          </p>
          {globalMessage && <div className="alert success">{globalMessage}</div>}
          {formError && <div className="alert">{formError}</div>}
          {codeError && <div className="alert">{codeError}</div>}
          <form onSubmit={handleSubmitCode(handleVerify)} className="otp-form">
            <label htmlFor="code">Код из письма</label>
            <input
              id="code"
              className="code-input"
              inputMode="numeric"
              maxLength={6}
              {...registerCode('code', { required: 'Введите код подтверждения' })}
            />
            {codeErrors.code && <p className="error-text">{codeErrors.code.message}</p>}
            <label className="checkbox" htmlFor="auto_login">
              <input type="checkbox" id="auto_login" {...registerCode('auto_login')} />
              Войти автоматически после подтверждения
            </label>
            <div className="otp-meta">
              <span className="status-chip">Попыток осталось: {attemptsLeft}</span>
              <span className="muted-text">Код можно запросить не чаще раза в минуту</span>
            </div>
            <div className="form-actions">
              <button className="button primary" type="submit" disabled={isVerifying}>
                {isVerifying ? 'Проверяем…' : 'Подтвердить'}
              </button>
              <button className="button secondary" type="button" onClick={resetFlow}>
                Изменить данные
              </button>
            </div>
          </form>
          <div className="resend-box">
            <p>Не пришёл код?</p>
            <button
              className="button ghost"
              type="button"
              onClick={handleResend}
              disabled={cooldown > 0 || resendLoading}
            >
              {cooldown > 0 ? `Отправлено (${cooldown}s)` : resendLoading ? 'Отправляем…' : 'Отправить ещё раз'}
            </button>
          </div>
        </>
      )}

      {step === 'success' && (
        <>
          <h1>Почта подтверждена</h1>
          {successMessage && <div className="alert success">{successMessage}</div>}
          <p>
            Учётная запись создана. Теперь можно{' '}
            <Link to="/login">войти в систему</Link> и заполнить профиль.
          </p>
          <div className="form-actions">
            <Link className="button primary" to="/login">
              Перейти ко входу
            </Link>
            <button className="button secondary" type="button" onClick={resetFlow}>
              Создать другой аккаунт
            </button>
          </div>
        </>
      )}

      <div className="muted-text" style={{ marginTop: '1.5rem' }}>
        Уже есть аккаунт? <Link to="/login">Войдите</Link>
      </div>
    </div>
  );
}
