import { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function PublicProfilePage() {
  const { locale } = useLocale();
  const { slug } = useParams();
  const profile = useMemo(() => publicContent[locale].profiles.find((item) => item.slug === slug) ?? publicContent[locale].profiles[0], [locale, slug]);
  const seo = publicContent[locale].seo.profile;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: profile.name,
    jobTitle: profile.title,
    worksFor: publicContent[locale].organization.name,
    address: profile.location,
    description: profile.bio,
    knowsAbout: profile.skills,
  };

  return (
    <div className="card" data-analytics-id="profile">
      <SeoHelmet title={`${profile.name} — ${seo.title}`} description={seo.description} path={`/profiles/${profile.slug}`} ogImage="https://cdn.obsidianfreelance.com/meta/profile.png" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{profile.name}</h1>
          <p>{profile.title}</p>
        </div>
        <div className="badge-row">
          <span className="badge">{profile.location}</span>
          <span className="badge">{profile.rate}</span>
          <span className="badge">{profile.availability}</span>
        </div>
      </header>
      <p>{profile.bio}</p>
      <section className="card" style={{ marginTop: '1.5rem' }}>
        <h2>{locale === 'uz' ? 'Ko‘nikmalar' : 'Навыки'}</h2>
        <div className="skill-pills">
          {profile.skills.map((skill) => (
            <span key={skill} className="skill-pill">
              {skill}
            </span>
          ))}
        </div>
      </section>
      <section className="card" style={{ marginTop: '1.5rem' }}>
        <h2>{locale === 'uz' ? 'Portfolio' : 'Портфолио'}</h2>
        <div className="grid two">
          {profile.portfolio.map((item) => (
            <article key={item.title} className="portfolio-card">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="card" style={{ marginTop: '1.5rem' }}>
        <h2>{locale === 'uz' ? 'Izohlar' : 'Отзывы'}</h2>
        <div className="grid two">
          {profile.testimonials.map((item) => (
            <blockquote key={item.author}>
              <p>“{item.text}”</p>
              <footer>{item.author}</footer>
            </blockquote>
          ))}
        </div>
      </section>
    </div>
  );
}
