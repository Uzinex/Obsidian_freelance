import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  fetchProfile,
  fetchSkills,
  upsertProfile,
  logout as logoutRequest,
  applyAuthToken,
  fetchWallet,
  depositWallet,
  withdrawWallet,
  fetchContracts,
  signContract,
  completeContract,
  requestContractTermination,
} from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import SkillSelector from '../components/SkillSelector.jsx';
import NotificationCenter from '../components/notifications/NotificationCenter.jsx';
import { formatCurrency, formatDateTime } from '../utils/formatting.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const roleOptions = [
  { value: 'freelancer', label: 'Фрилансер' },
  { value: 'client', label: 'Заказчик' },
];

const freelancerTypes = [
  { value: 'individual', label: 'Индивидуальный специалист' },
  { value: 'company', label: 'Компания' },
];

const registrationTypes = [
  { value: 'none', label: 'Не зарегистрирована' },
  { value: 'mchj', label: 'MCHJ' },
  { value: 'yatt', label: 'YATT' },
];

function resolveAvatar(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}${url}`;
}

function composeName(user) {
  if (!user) return '';
  const parts = [user.first_name, user.last_name].filter(Boolean);
  if (parts.length) return parts.join(' ');
  return user.nickname || 'Пользователь';
}

function getProfileFormDefaults(profile) {
  return {
    role: profile?.role || 'freelancer',
    freelancer_type: profile?.freelancer_type || 'individual',
    company_registered_as: profile?.company_registered_as || 'none',
    skills: profile?.skills || [],
    phone_number: profile?.phone_number || '',
    company_name: profile?.company_name || '',
    company_country: profile?.company_country || '',
    company_city: profile?.company_city || '',
    company_street: profile?.company_street || '',
    company_tax_id: profile?.company_tax_id || '',
    country: profile?.country || '',
    city: profile?.city || '',
    street: profile?.street || '',
    house: profile?.house || '',
    avatar: null,
  };
}

export default function ProfilePage() {
  const { user, login, token, logout, isVerificationAdmin } = useAuth();
  const { buildPath, locale } = useLocale();
  const [skills, setSkills] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [avatarPreview, setAvatarPreview] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');
  const [wallet, setWallet] = useState(null);
  const [contracts, setContracts] = useState([]);
  const [walletMessage, setWalletMessage] = useState('');
  const [walletError, setWalletError] = useState('');
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [contractMessage, setContractMessage] = useState('');
  const [contractError, setContractError] = useState('');
  const profile = user?.profile;
  const profileDefaults = useMemo(() => getProfileFormDefaults(profile), [profile]);

  const form = useForm({
    defaultValues: profileDefaults,
  });

  useEffect(() => {
    form.reset(profileDefaults);
    setAvatarPreview(resolveAvatar(profile?.avatar));
  }, [profileDefaults, profile, form]);

  useEffect(() => {
    async function loadData() {
      try {
        const [skillData, profileData] = await Promise.all([
          fetchSkills(),
          profile ? Promise.resolve(profile) : fetchProfile(),
        ]);
        setSkills(skillData.results || skillData);
        const freshProfile = profile || profileData;
        if (!profile && freshProfile) {
          login(token, { ...user, profile: freshProfile });
        }
        setAvatarPreview(resolveAvatar(freshProfile?.avatar));
      } catch (err) {
        console.error('Не удалось загрузить профиль', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [profile, token, user, login]);

  useEffect(() => {
    async function loadSupplementaryData() {
      if (!token) return;
      try {
        const [walletData, contractData] = await Promise.all([
          fetchWallet({ limit: 10 }),
          fetchContracts(),
        ]);
        setWallet(walletData);
        const contractList = contractData.results || contractData;
        setContracts(Array.isArray(contractList) ? contractList : []);
      } catch (supplementaryError) {
        console.error('Не удалось загрузить финансовые данные', supplementaryError);
      }
    }
    loadSupplementaryData();
  }, [token, profile?.id]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const currentRole = form.watch('role');
  const freelancerType = form.watch('freelancer_type');

  const handleAvatarChange = (event) => {
    const file = event.target.files?.[0];
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl('');
    }
    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
      setAvatarPreview(objectUrl);
    } else {
      setAvatarPreview(resolveAvatar(profile?.avatar));
    }
  };

  async function onSubmit(data) {
    try {
      setError('');
      setMessage('');
      const payload = {
        ...data,
        skills: (data.skills || []).map((item) => Number(item)),
      };
      delete payload.avatar;

      const updated = await upsertProfile(payload, profile?.id);
      let finalProfile = updated;

      const avatarFile = data.avatar?.[0];
      if (avatarFile) {
        const formData = new FormData();
        formData.append('avatar', avatarFile);
        finalProfile = await upsertProfile(formData, updated.id || profile?.id);
      }

      login(token, { ...user, profile: finalProfile });
      form.reset(getProfileFormDefaults(finalProfile));
      setAvatarPreview(resolveAvatar(finalProfile.avatar));
      setIsEditing(false);
      setMessage('Профиль успешно сохранен.');
    } catch (err) {
      console.error(err);
      setError('Ошибка при сохранении профиля.');
    }
  }

  const isVerified = Boolean(profile?.is_verified);
  const verificationLabel = isVerified ? 'Верифицирован' : 'Не верифицирован';

  const handleEditToggle = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl('');
    }
    form.reset(profileDefaults);
    setAvatarPreview(resolveAvatar(profile?.avatar));
    setIsEditing((prev) => !prev);
  };

  const handleLogout = async () => {
    try {
      await logoutRequest();
    } catch (logoutError) {
      console.warn('Failed to logout from API', logoutError);
    }
    applyAuthToken(null);
    logout();
  };

  function extractErrorMessage(err, fallback) {
    if (err?.response?.data?.detail) return err.response.data.detail;
    if (Array.isArray(err?.response?.data?.non_field_errors)) {
      return err.response.data.non_field_errors.join(' ');
    }
    if (err?.message) return err.message;
    return fallback;
  }

  const refreshWallet = async () => {
    const data = await fetchWallet({ limit: 10 });
    setWallet(data);
  };

  const handleDeposit = async () => {
    if (!depositAmount) return;
    try {
      setWalletError('');
      setWalletMessage('');
      await depositWallet({ amount: Number(depositAmount) });
      await refreshWallet();
      setDepositAmount('');
      setWalletMessage('Кошелёк успешно пополнен.');
    } catch (err) {
      setWalletError(extractErrorMessage(err, 'Не удалось пополнить кошелёк.'));
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawAmount) return;
    try {
      setWalletError('');
      setWalletMessage('');
      await withdrawWallet({ amount: Number(withdrawAmount) });
      await refreshWallet();
      setWithdrawAmount('');
      setWalletMessage('Средства успешно списаны.');
    } catch (err) {
      setWalletError(extractErrorMessage(err, 'Не удалось выполнить списание.'));
    }
  };

  const handleContractSign = async (id) => {
    try {
      setContractError('');
      setContractMessage('');
      const updated = await signContract(id);
      setContracts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setContractMessage('Контракт успешно подписан.');
    } catch (err) {
      setContractError(extractErrorMessage(err, 'Не удалось подписать контракт.'));
    }
  };

  const handleContractComplete = async (id) => {
    try {
      setContractError('');
      setContractMessage('');
      const updated = await completeContract(id);
      setContracts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setContractMessage('Заказ завершён и выплата отправлена.');
      await refreshWallet();
    } catch (err) {
      setContractError(extractErrorMessage(err, 'Не удалось завершить контракт.'));
    }
  };

  const handleContractTermination = async (id) => {
    const reason = window.prompt('Укажите причину расторжения контракта');
    if (!reason) return;
    try {
      setContractError('');
      setContractMessage('');
      const updated = await requestContractTermination(id, { reason });
      setContracts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setContractMessage('Запрос на расторжение отправлен на рассмотрение.');
    } catch (err) {
      setContractError(extractErrorMessage(err, 'Не удалось отправить запрос на расторжение.'));
    }
  };

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  const summarySkills = profile?.skill_details || [];
  const displayName = composeName(profile?.user || user);
  const roleLabel = roleOptions.find((option) => option.value === profile?.role)?.label;

  return (
    <div className="profile-page">
      <section className="card profile-summary">
        <div className="profile-summary-header">
          <div className="profile-avatar">
            {avatarPreview ? (
              <img src={avatarPreview} alt={displayName} loading="lazy" decoding="async" />
            ) : (
              <span>{displayName ? displayName.charAt(0) : '?'}</span>
            )}
          </div>
          <div>
            <h1>{displayName}</h1>
            <div className="profile-verification">
              <span className={`verification-badge ${isVerified ? 'verified' : 'unverified'}`}>{verificationLabel}</span>
            </div>
            {roleLabel && <p className="profile-role">{roleLabel}</p>}
            {profile?.freelancer_type && (
              <p className="profile-role subtle">
                {profile.freelancer_type === 'company' ? 'Команда фрилансеров' : 'Индивидуальный специалист'}
              </p>
            )}
          </div>
          <div className="profile-actions">
            {!isVerificationAdmin && !isVerified && (
              <Link to={buildPath('/verification')} className="button ghost">
                Пройти верификацию
              </Link>
            )}
            {isVerificationAdmin && (
              <>
                <Link to={buildPath('/verification')} className="button ghost">
                  Верификация
                </Link>
                <Link to={buildPath('/verification/requests')} className="button ghost">
                  Заявки
                </Link>
              </>
            )}
            <button type="button" className="button secondary" onClick={handleEditToggle}>
              {isEditing ? 'Отменить' : 'Редактировать профиль'}
            </button>
            <button type="button" className="button ghost" onClick={handleLogout}>
              Выйти
            </button>
          </div>
        </div>
        <div className="profile-summary-grid">
          <div>
            <h3>Контакты</h3>
            <p>
              <strong>Телефон:</strong> {profile?.phone_number || 'не указан'}
            </p>
            <p>
              <strong>Email:</strong> {profile?.user?.email || user?.email}
            </p>
            <p>
              <strong>Адрес:</strong>{' '}
              {[profile?.country, profile?.city, profile?.street, profile?.house].filter(Boolean).join(', ') || 'не указан'}
            </p>
          </div>
          <div>
            <h3>Навыки</h3>
            <div className="profile-skills">
              {summarySkills.length ? (
                summarySkills.map((skill) => (
                  <span key={skill.id} className="tag">
                    {skill.name}
                  </span>
                ))
              ) : (
                <p className="subtle">Навыки не указаны</p>
              )}
            </div>
          </div>
          {profile?.freelancer_type === 'company' && (
            <div>
              <h3>Компания</h3>
              <p>
                <strong>{profile?.company_name}</strong>
              </p>
              <p>
                {[
                  profile?.company_country,
                  profile?.company_city,
                  profile?.company_street,
                ]
                  .filter(Boolean)
                  .join(', ') || 'Адрес не указан'}
              </p>
              {profile?.company_tax_id && <p>ИНН: {profile.company_tax_id}</p>}
            </div>
          )}
        </div>
      </section>

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}

      <section className="card wallet-card">
        <div className="wallet-header">
          <div>
            <h2>Кошелёк</h2>
            <p className="subtle">Управляйте балансом в узбекских сумах (UZS)</p>
          </div>
          <div className="wallet-balance">
            {wallet ? formatCurrency(wallet.balance, { currency: wallet.currency, locale }) : '—'}
          </div>
        </div>
        {walletMessage && <div className="alert success">{walletMessage}</div>}
        {walletError && <div className="alert">{walletError}</div>}
        <div className="wallet-actions">
          <div className="wallet-action">
            <label htmlFor="wallet-deposit">Пополнить кошелёк</label>
            <div className="wallet-action-row">
              <input
                id="wallet-deposit"
                type="number"
                min="0"
                step="0.01"
                value={depositAmount}
                onChange={(event) => setDepositAmount(event.target.value)}
                placeholder="Введите сумму"
              />
              <button type="button" className="button primary" onClick={handleDeposit}>
                Пополнить
              </button>
            </div>
          </div>
          <div className="wallet-action">
            <label htmlFor="wallet-withdraw">Вывести средства</label>
            <div className="wallet-action-row">
              <input
                id="wallet-withdraw"
                type="number"
                min="0"
                step="0.01"
                value={withdrawAmount}
                onChange={(event) => setWithdrawAmount(event.target.value)}
                placeholder="Введите сумму"
              />
              <button type="button" className="button secondary" onClick={handleWithdraw}>
                Списать
              </button>
            </div>
          </div>
        </div>
        <div className="wallet-transactions">
          <h3>Последние операции</h3>
          {wallet?.transactions?.length ? (
            <ul>
              {wallet.transactions.map((transaction) => {
                const amount = Number(transaction.amount);
                const formattedAmount = formatCurrency(Math.abs(amount), {
                  currency: wallet.currency,
                  locale,
                });
                const sign = amount >= 0 ? '+' : '−';
                return (
                  <li key={transaction.id}>
                    <div>
                      <strong>{transaction.type}</strong>
                      <span>{formatDateTime(transaction.created_at)}</span>
                      {transaction.description && <p className="subtle">{transaction.description}</p>}
                    </div>
                    <div className="wallet-transaction-amount">
                      <span className={amount >= 0 ? 'positive' : 'negative'}>
                        {sign} {formattedAmount}
                      </span>
                      <small>
                        Баланс: {formatCurrency(transaction.balance_after, { currency: wallet.currency, locale })}
                      </small>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="subtle">Операции кошелька пока отсутствуют.</p>
          )}
        </div>
      </section>

      <section className="card notifications-card">
        <NotificationCenter />
      </section>

      <section className="card contracts-card">
        <div className="contracts-header">
          <h2>Контракты</h2>
        </div>
        {contractMessage && <div className="alert success">{contractMessage}</div>}
        {contractError && <div className="alert">{contractError}</div>}
        {contracts.length ? (
          <ul className="contracts-list">
            {contracts.map((contract) => {
              const roleText = contract.user_role === 'client' ? 'Вы — заказчик' : 'Вы — исполнитель';
              return (
                <li key={contract.id} className={`contract-item status-${contract.status}`}>
                  <header>
                    <div>
                      <h3>{contract.order_title}</h3>
                      <p className="subtle">{roleText}</p>
                    </div>
                    <span className="contract-status">{contract.status_display}</span>
                  </header>
                  <p>
                    <strong>Сумма:</strong> {formatCurrency(contract.budget_snapshot, {
                      currency: contract.currency,
                      locale,
                    })}
                  </p>
                  <p>
                    <strong>Подписание:</strong> заказчик —{' '}
                    {contract.client_signed ? 'подписано' : 'ожидает'}, исполнитель —{' '}
                    {contract.freelancer_signed ? 'подписано' : 'ожидает'}
                  </p>
                  {contract.termination_requested && (
                    <p className="subtle">
                      Запрос на расторжение: {contract.termination_requested_by === 'client' ? 'заказчик' : 'фрилансер'} —{' '}
                      {contract.termination_reason || 'ожидает комментария'}
                    </p>
                  )}
                  <div className="contract-actions">
                    {contract.can_sign && (
                      <button
                        type="button"
                        className="button primary"
                        onClick={() => handleContractSign(contract.id)}
                      >
                        Подписать контракт
                      </button>
                    )}
                    {contract.can_complete && (
                      <button
                        type="button"
                        className="button secondary"
                        onClick={() => handleContractComplete(contract.id)}
                      >
                        Завершить контракт
                      </button>
                    )}
                    {contract.can_request_termination && (
                      <button
                        type="button"
                        className="button ghost"
                        onClick={() => handleContractTermination(contract.id)}
                      >
                        Расторгнуть контракт
                      </button>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="subtle">У вас пока нет контрактов.</p>
        )}
      </section>

      {isEditing && (
        <section className="card profile-form-card">
          <h2>Редактирование профиля</h2>
          <form onSubmit={form.handleSubmit(onSubmit)} className="profile-form">
            <div className="form-grid">
              <div className="form-section">
                <h3>Основная информация</h3>
                <label htmlFor="role">Роль</label>
                <select id="role" {...form.register('role')}>
                  {roleOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {currentRole === 'freelancer' && (
                  <>
                    <label htmlFor="freelancer_type">Тип</label>
                    <select id="freelancer_type" {...form.register('freelancer_type')}>
                      {freelancerTypes.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </>
                )}
                <label htmlFor="phone_number">Телефон</label>
                <input id="phone_number" {...form.register('phone_number')} placeholder="+998 90 000 00 00" />
                <label htmlFor="avatar">Фото профиля</label>
                {(() => {
                  const avatarField = form.register('avatar');
                  return (
                    <input
                      id="avatar"
                      type="file"
                      accept="image/*"
                      {...avatarField}
                      onChange={(event) => {
                        avatarField.onChange(event);
                        handleAvatarChange(event);
                      }}
                    />
                  );
                })()}
              </div>

              <div className="form-section">
                <h3>Адрес</h3>
                <label htmlFor="country">Страна проживания</label>
                <input id="country" {...form.register('country')} />
                <label htmlFor="city">Город</label>
                <input id="city" {...form.register('city')} />
                <label htmlFor="street">Улица</label>
                <input id="street" {...form.register('street')} />
                <label htmlFor="house">Дом / квартира</label>
                <input id="house" {...form.register('house')} />
              </div>

              {currentRole === 'freelancer' && (
                <div className="form-section">
                  <h3>Навыки и специализация</h3>
                  <SkillSelector control={form.control} name="skills" skills={skills} />
                </div>
              )}

              {currentRole === 'freelancer' && freelancerType === 'company' && (
                <div className="form-section">
                  <h3>Данные компании</h3>
                  <label htmlFor="company_name">Название компании</label>
                  <input id="company_name" {...form.register('company_name')} />
                  <label htmlFor="company_registered_as">Регистрация</label>
                  <select id="company_registered_as" {...form.register('company_registered_as')}>
                    {registrationTypes.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                  <label htmlFor="company_tax_id">ИНН компании</label>
                  <input id="company_tax_id" {...form.register('company_tax_id')} />
                  <label htmlFor="company_country">Страна компании</label>
                  <input id="company_country" {...form.register('company_country')} />
                  <label htmlFor="company_city">Город компании</label>
                  <input id="company_city" {...form.register('company_city')} />
                  <label htmlFor="company_street">Улица компании</label>
                  <input id="company_street" {...form.register('company_street')} />
                </div>
              )}
            </div>

            <div className="form-actions">
              <button className="button primary" type="submit">
                Сохранить
              </button>
            </div>
          </form>
        </section>
      )}
    </div>
  );
}
