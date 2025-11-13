import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { fetchProfile, fetchSkills, upsertProfile } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

const roleOptions = [
  { value: 'freelancer', label: 'Фрилансер' },
  { value: 'client', label: 'Заказчик' },
];

const freelancerTypes = [
  { value: 'individual', label: 'Единый фрилансер' },
  { value: 'company', label: 'Компания' },
];

const registrationTypes = [
  { value: 'none', label: 'Не зарегистрирована' },
  { value: 'mchj', label: 'MCHJ' },
  { value: 'yatt', label: 'YATT' },
];

export default function ProfilePage() {
  const { user, login, token } = useAuth();
  const [skills, setSkills] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const profile = user?.profile;

  const form = useForm({
    defaultValues: useMemo(
      () => ({
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
      }),
      [profile],
    ),
  });

  useEffect(() => {
    form.reset({
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
    });
  }, [profile, form]);

  useEffect(() => {
    async function loadData() {
      try {
        const [skillData, profileData] = await Promise.all([
          fetchSkills(),
          profile ? Promise.resolve(profile) : fetchProfile(),
        ]);
        setSkills(skillData);
        if (!profile && profileData) {
          login(token, { ...user, profile: profileData });
        }
      } catch (err) {
        console.error('Не удалось загрузить профиль', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [profile, token, user, login]);

  const currentRole = form.watch('role');
  const freelancerType = form.watch('freelancer_type');

  async function onSubmit(data) {
    try {
      setError('');
      setMessage('');
      const payload = {
        ...data,
        skills: (data.skills || []).map((item) => Number(item)),
      };
      const updated = await upsertProfile(payload, profile?.id);
      login(token, { ...user, profile: updated });
      setMessage('Профиль успешно сохранен.');
    } catch (err) {
      console.error(err);
      setError('Ошибка при сохранении профиля.');
    }
  }

  if (loading) {
    return <div className="card">Загрузка...</div>;
  }

  return (
    <div className="card">
      <h1>Профиль</h1>
      <p>Заполните информацию, чтобы получить доступ ко всем функциям платформы.</p>
      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}
      <form onSubmit={form.handleSubmit(onSubmit)} className="grid two">
        <div>
          <label htmlFor="role">Роль</label>
          <select id="role" {...form.register('role')}>
            {roleOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        {currentRole === 'freelancer' && (
          <div>
            <label htmlFor="freelancer_type">Тип</label>
            <select id="freelancer_type" {...form.register('freelancer_type')}>
              {freelancerTypes.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}
        {currentRole === 'freelancer' && freelancerType === 'company' && (
          <>
            <div>
              <label htmlFor="company_name">Название компании</label>
              <input id="company_name" {...form.register('company_name')} />
            </div>
            <div>
              <label htmlFor="company_registered_as">Регистрация</label>
              <select id="company_registered_as" {...form.register('company_registered_as')}>
                {registrationTypes.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="company_tax_id">ИНН компании</label>
              <input id="company_tax_id" {...form.register('company_tax_id')} />
            </div>
            <div>
              <label htmlFor="company_country">Страна компании</label>
              <input id="company_country" {...form.register('company_country')} />
            </div>
            <div>
              <label htmlFor="company_city">Город компании</label>
              <input id="company_city" {...form.register('company_city')} />
            </div>
            <div>
              <label htmlFor="company_street">Улица компании</label>
              <input id="company_street" {...form.register('company_street')} />
            </div>
          </>
        )}

        <div>
          <label htmlFor="phone_number">Телефон</label>
          <input id="phone_number" {...form.register('phone_number')} placeholder="+998 90 000 00 00" />
        </div>

        <div>
          <label htmlFor="country">Страна проживания</label>
          <input id="country" {...form.register('country')} />
        </div>
        <div>
          <label htmlFor="city">Город</label>
          <input id="city" {...form.register('city')} />
        </div>
        <div>
          <label htmlFor="street">Улица</label>
          <input id="street" {...form.register('street')} />
        </div>
        <div>
          <label htmlFor="house">Дом / квартира</label>
          <input id="house" {...form.register('house')} />
        </div>

        {currentRole === 'freelancer' && (
          <div style={{ gridColumn: '1 / -1' }}>
            <label htmlFor="skills">Навыки</label>
            <select id="skills" multiple size={Math.min(skills.length, 12)} {...form.register('skills')}>
              {skills.map((skill) => (
                <option key={skill.id} value={skill.id}>
                  {skill.name}
                </option>
              ))}
            </select>
            <small>Зажмите Ctrl / Cmd для выбора нескольких навыков.</small>
          </div>
        )}

        <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
          <button className="button primary" type="submit">
            Сохранить
          </button>
        </div>
      </form>
    </div>
  );
}
