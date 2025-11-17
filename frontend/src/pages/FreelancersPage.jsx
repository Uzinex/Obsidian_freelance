import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchCategories, apiClient } from '../api/client.js';
import SeoHelmet from '../components/SeoHelmet.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import { publicContent } from '../mocks/publicContent.js';
import Icon from '../components/Icon.jsx';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function resolveAvatar(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return `${API_BASE_URL}${url}`;
}

function buildAvatarSrcSet(src) {
  if (!src) {
    return undefined;
  }
  const separator = src.includes('?') ? '&' : '?';
  const baseSize = 96;
  return [1, 2].map((scale) => `${src}${separator}w=${baseSize * scale} ${scale}x`).join(', ');
}

const PROFILE_FAQ = {
  ru: [
    {
      question: 'Как проходит верификация специалиста?',
      answer: 'Мы проверяем документы, портфолио и минимум одну рекомендацию, после чего выдаём бейдж и SLA по ответу.',
    },
    {
      question: 'Можно ли создать командный профиль?',
      answer: 'Да, объединяйте нескольких специалистов в одну карточку с прозрачной ставкой и расписанием.',
    },
  ],
  uz: [
    {
      question: 'Mutaxassis qanday tekshiruvdan o‘tadi?',
      answer: 'Hujjatlar, portfolio va kamida bitta tavsiyanoma tekshiriladi, so‘ng verifikatsiya belgisi qo‘yiladi.',
    },
    {
      question: 'Jamoaviy profil ochsa bo‘ladimi?',
      answer: 'Ha, bir nechta mutaxassisni yagona profilga birlashtirib, stavka va bandlikni ko‘rsating.',
    },
  ],
};

export default function FreelancersPage() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const { locale, buildPath, buildAbsoluteUrl } = useLocale();
  const seo = publicContent[locale].seo.freelancers;
  const faq = PROFILE_FAQ[locale];

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

  const breadcrumbLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        {
          '@type': 'ListItem',
          position: 1,
          name: 'Главная',
          item: publicContent[locale].organization.url,
        },
        {
          '@type': 'ListItem',
          position: 2,
          name: seo.title,
          item: `${publicContent[locale].organization.url}/freelancers`,
        },
      ],
    }),
    [locale, seo.title],
  );

  const itemListLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      itemListElement: filteredProfiles.slice(0, 12).map((profile, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        url: buildAbsoluteUrl(`/profiles/${profile.slug || profile.id}`),
        name: profile.user?.first_name || profile.user?.nickname || 'Freelancer',
      })),
    }),
    [filteredProfiles, buildPath],
  );

  const faqLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faq.map((entry) => ({
        '@type': 'Question',
        name: entry.question,
        acceptedAnswer: { '@type': 'Answer', text: entry.answer },
      })),
    }),
    [faq],
  );

  const jsonLd = useMemo(() => [breadcrumbLd, itemListLd, faqLd], [breadcrumbLd, itemListLd, faqLd]);

  return (
    <div className="freelancers-page">
      <SeoHelmet title={seo.title} description={seo.description} path="/freelancers" jsonLd={jsonLd} />
      <section className="card filter-card">
        <h1>{seo.title}</h1>
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
            const avatar = resolveAvatar(profile.avatar);
            const profileUrl = buildPath(`/profiles/${profile.slug || profile.id}`);
            return (
              <article key={profile.id} className="person-card">
                <div className="person-avatar" aria-hidden="true">
                  {profile.avatar ? (
                    <img
                      src={avatar}
                      srcSet={buildAvatarSrcSet(avatar)}
                      sizes="(max-width: 600px) 96px, 128px"
                      alt={name}
                      loading="lazy"
                      decoding="async"
                    />
                  ) : (
                    <span>{name?.charAt(0) || '?'}</span>
                  )}
                </div>
                <div className="person-info">
                  <h2>{name}</h2>
                  <div className="person-verification">
                    <Icon name={isVerified ? 'check' : 'info'} size={18} decorative />
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
                  <div className="person-actions">
                    <Link to={profileUrl} className="button ghost">
                      Профиль
                    </Link>
                  </div>
                </div>
                <div className="person-preview">
                  <p>{profile.bio || 'Команда обновит описание в ближайшее время.'}</p>
                  <div className="person-preview-meta">
                    {profile.rate && <span>Ставка: {profile.rate}</span>}
                    {profile.availability && <span>Доступность: {profile.availability}</span>}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}

      <section className="card faq-card" style={{ marginTop: '2rem' }}>
        <div className="section-header">
          <div>
            <h2>{locale === 'uz' ? 'Savollar' : 'FAQ по фрилансерам'}</h2>
            <p>{locale === 'uz' ? 'Kuratorlar va verifikatsiya haqida savollarga javoblar.' : 'Ответы про проверку и формат работы.'}</p>
          </div>
        </div>
        <div className="faq-list">
          {faq.map((entry) => (
            <article key={entry.question} className="faq-item">
              <h3>{entry.question}</h3>
              <p>{entry.answer}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
