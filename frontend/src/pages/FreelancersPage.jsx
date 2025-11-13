import { useEffect, useState } from 'react';
import { fetchSkills } from '../api/client.js';
import { apiClient } from '../api/client.js';

export default function FreelancersPage() {
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState('');
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSkills() {
      try {
        const data = await fetchSkills();
        setSkills(data);
      } catch (err) {
        console.error('Не удалось загрузить навыки', err);
      }
    }
    loadSkills();
  }, []);

  useEffect(() => {
    async function loadProfiles() {
      setLoading(true);
      try {
        const params = { role: 'freelancer' };
        if (selectedSkill) params.skill = selectedSkill;
        const { data } = await apiClient.get('accounts/profiles/', { params });
        setProfiles(data);
      } catch (err) {
        console.error('Не удалось загрузить фрилансеров', err);
      } finally {
        setLoading(false);
      }
    }
    loadProfiles();
  }, [selectedSkill]);

  return (
    <div className="grid" style={{ gap: '2rem' }}>
      <section className="card">
        <h1>Найдите фрилансера</h1>
        <label htmlFor="skillFilter">Фильтр по навыкам</label>
        <select id="skillFilter" value={selectedSkill} onChange={(event) => setSelectedSkill(event.target.value)}>
          <option value="">Все навыки</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>
      </section>

      {loading ? (
        <div className="card">Загрузка фрилансеров...</div>
      ) : (
        <div className="grid two">
          {profiles.map((profile) => (
            <article key={profile.id} className="card">
              <h2>{profile.user?.first_name} {profile.user?.last_name}</h2>
              <div className="status">{profile.freelancer_type === 'company' ? 'Компания' : 'Фрилансер'}</div>
              <p>
                <strong>Никнейм:</strong> {profile.user?.nickname}
              </p>
              <p>
                <strong>Телефон:</strong> {profile.phone_number || 'не указан'}
              </p>
              <p>
                <strong>Адрес:</strong> {[profile.country, profile.city, profile.street].filter(Boolean).join(', ') || 'не указан'} {profile.house || ''}
              </p>
              <div style={{ marginTop: '1rem' }}>
                {profile.skill_details?.map((skill) => (
                  <span key={skill.id} className="tag">
                    {skill.name}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
