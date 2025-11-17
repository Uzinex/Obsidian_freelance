import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';
import { apiClient } from '../../api/client.js';

const availabilityLabels = {
  ru: {
    full_time: 'Доступен фултайм',
    part_time: 'Частичная занятость',
    project: 'Проектная работа',
  },
  uz: {
    full_time: 'To‘liq bandlik',
    part_time: 'Qisman bandlik',
    project: 'Loyiha asosida',
  },
};

function buildName(user) {
  if (!user) return '';
  const parts = [user.first_name, user.last_name].filter(Boolean);
  if (parts.length === 0) {
    return user.nickname || '';
  }
  return parts.join(' ');
}

function formatLocation(profile) {
  if (profile.location && typeof profile.location === 'object') {
    const values = [profile.location.city, profile.location.country].filter(Boolean);
    if (values.length) return values.join(', ');
  }
  const fallback = [profile.city, profile.country].filter(Boolean);
  return fallback.join(', ');
}

function formatRate(profile, locale) {
  const value = profile.hourly_rate;
  if (value === null || value === undefined || value === '') {
    return '';
  }
  const currency = profile.wallet?.currency || 'UZS';
  try {
    const numericValue = typeof value === 'number' ? value : Number(value);
    if (Number.isFinite(numericValue)) {
      const formatter = new Intl.NumberFormat(locale === 'uz' ? 'uz-UZ' : 'ru-RU', {
        style: 'currency',
        currency,
        maximumFractionDigits: 2,
      });
      return `${formatter.format(numericValue)}/час`;
    }
  } catch (error) {
    console.warn('Не удалось отформатировать ставку', error);
  }
  return `${value} ${currency}`;
}

function mapApiProfile(data, locale) {
  return {
    id: data.id,
    slug: data.slug,
    name: buildName(data.user) || 'Freelancer',
    title: data.headline || (locale === 'uz' ? 'Mutaxassis profili' : 'Профиль специалиста'),
    location: formatLocation(data),
    rate: formatRate(data, locale),
    availability: availabilityLabels[locale]?.[data.availability] || '',
    bio: data.bio || '',
    skills: Array.isArray(data.skill_details) ? data.skill_details.map((skill) => skill.name) : [],
    portfolio: [],
    testimonials: [],
  };
}

export default function PublicProfilePage() {
  const { locale } = useLocale();
  const { slug } = useParams();
  const seo = publicContent[locale].seo.profile;
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const fallbackProfile = useMemo(
    () => publicContent[locale].profiles.find((item) => item.slug === slug) ?? null,
    [locale, slug],
  );

  useEffect(() => {
    let isMounted = true;
    async function fetchProfile() {
      setLoading(true);
      setError('');
      try {
        const endpoint = /^\d+$/.test(slug)
          ? `accounts/profiles/${slug}/`
          : `accounts/profiles/public/${slug}/`;
        const { data } = await apiClient.get(endpoint);
        if (isMounted) {
          setProfile(mapApiProfile(data, locale));
        }
      } catch (err) {
        console.error('Не удалось загрузить профиль', err);
        if (isMounted) {
          if (fallbackProfile) {
            setProfile(fallbackProfile);
          } else {
            setError(locale === 'uz' ? 'Profil topilmadi' : 'Профиль не найден');
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }
    fetchProfile();
    return () => {
      isMounted = false;
    };
  }, [slug, locale, fallbackProfile]);

  if (loading) {
    return <div className="card">{locale === 'uz' ? 'Profil yuklanmoqda...' : 'Загрузка профиля...'}</div>;
  }

  if (error) {
    return <div className="card">{error}</div>;
  }

  const currentProfile = profile || fallbackProfile;

  if (!currentProfile) {
    return <div className="card">{locale === 'uz' ? 'Profil topilmadi' : 'Профиль не найден'}</div>;
  }

  const organization = publicContent[locale].organization;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: currentProfile.name,
    jobTitle: currentProfile.title,
    worksFor: organization.name,
    address: currentProfile.location,
    description: currentProfile.bio,
    knowsAbout: currentProfile.skills,
  };

  return (
    <div className="card" data-analytics-id="profile">
      <SeoHelmet
        title={`${currentProfile.name} — ${seo.title}`}
        description={seo.description}
        path={`/profiles/${currentProfile.slug || slug}`}
        ogImage="https://cdn.obsidianfreelance.com/meta/profile.png"
        jsonLd={jsonLd}
      />
      <header className="section-header">
        <div>
          <h1>{currentProfile.name}</h1>
          {currentProfile.title && <p>{currentProfile.title}</p>}
        </div>
        <div className="badge-row">
          {currentProfile.location && <span className="badge">{currentProfile.location}</span>}
          {currentProfile.rate && <span className="badge">{currentProfile.rate}</span>}
          {currentProfile.availability && <span className="badge">{currentProfile.availability}</span>}
        </div>
      </header>
      {currentProfile.bio && <p>{currentProfile.bio}</p>}
      {Array.isArray(currentProfile.skills) && currentProfile.skills.length > 0 && (
        <section className="card" style={{ marginTop: '1.5rem' }}>
          <h2>{locale === 'uz' ? 'Ko‘nikmalar' : 'Навыки'}</h2>
          <div className="skill-pills">
            {currentProfile.skills.map((skill) => (
              <span key={skill} className="skill-pill">
                {skill}
              </span>
            ))}
          </div>
        </section>
      )}
      {currentProfile.portfolio?.length > 0 && (
        <section className="card" style={{ marginTop: '1.5rem' }}>
          <h2>{locale === 'uz' ? 'Portfolio' : 'Портфолио'}</h2>
          <div className="grid two">
            {currentProfile.portfolio.map((item) => (
              <article key={item.title} className="portfolio-card">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </section>
      )}
      {currentProfile.testimonials?.length > 0 && (
        <section className="card" style={{ marginTop: '1.5rem' }}>
          <h2>{locale === 'uz' ? 'Izohlar' : 'Отзывы'}</h2>
          <div className="grid two">
            {currentProfile.testimonials.map((item) => (
              <blockquote key={item.author}>
                <p>“{item.text}”</p>
                <footer>{item.author}</footer>
              </blockquote>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
