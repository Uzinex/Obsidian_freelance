import { useEffect, useMemo, useState } from 'react';
import { fetchCategories } from '../api/client.js';
import { apiClient } from '../api/client.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function resolveAvatar(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}${url}`;
}

export default function FreelancersPage() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInitial() {
      try {
        const [categoryData, { data }] = await Promise.all([
          fetchCategories(),
          apiClient.get('accounts/profiles/', { params: { role: 'freelancer' } }),
        ]);
        setCategories(categoryData.results || categoryData);
        setProfiles(Array.isArray(data.results) ? data.results : data);
      } catch (err) {
        console.error('Не удалось загрузить фрилансеров', err);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, []);

  const filteredProfiles = useMemo(() => {
    if (!selectedCategory) return profiles;
    return profiles.filter((profile) =>
      profile.skill_details?.some((skill) => skill.category?.toLowerCase() === selectedCategory.toLowerCase()),
    );
  }, [profiles, selectedCategory]);

  return (
    <div className="freelancers-page">
      <section className="card filter-card">
        <h1>Фрилансеры платформы</h1>
        <p>Соберите команду из специалистов, проверенных системой верификации Obsidian Freelance.</p>
        <div className="filter-chips">
          <button
            type="button"
            className={selectedCategory === '' ? 'chip active' : 'chip'}
            onClick={() => setSelectedCategory('')}
          >
            Все категории
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              type="button"
              className={selectedCategory === category.name ? 'chip active' : 'chip'}
              onClick={() => setSelectedCategory(category.name)}
            >
              {category.name}
            </button>
          ))}
        </div>
      </section>

      {loading ? (
        <div className="card">Загрузка фрилансеров...</div>
      ) : filteredProfiles.length === 0 ? (
        <div className="card empty-state">В выбранной категории пока нет специалистов. Попробуйте другую.</div>
      ) : (
        <div className="people-grid">
          {filteredProfiles.map((profile) => {
            const name = [profile.user?.first_name, profile.user?.last_name].filter(Boolean).join(' ') ||
              profile.user?.nickname;
            const location = [profile.country, profile.city].filter(Boolean).join(', ');
            const isVerified = Boolean(profile.is_verified);
            const verificationLabel = isVerified ? 'Верифицирован' : 'Не верифицирован';
            return (
              <article key={profile.id} className="person-card">
                <div className="person-avatar" aria-hidden="true">
                  {profile.avatar ? (
                    <img src={resolveAvatar(profile.avatar)} alt={name} />
                  ) : (
                    <span>{name?.charAt(0) || '?'}</span>
                  )}
                </div>
                <div className="person-info">
                  <h2>{name}</h2>
                  <div className="person-verification">
                    <span className={`verification-badge ${isVerified ? 'verified' : 'unverified'}`}>
                      {verificationLabel}
                    </span>
                  </div>
                  <p className="person-role">
                    {profile.freelancer_type === 'company' ? 'Команда фрилансеров' : 'Индивидуальный специалист'}
                  </p>
                  {location && <p className="person-location">{location}</p>}
                  <div className="person-skills">
                    {profile.skill_details?.slice(0, 6).map((skill) => (
                      <span key={skill.id} className="tag">
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
