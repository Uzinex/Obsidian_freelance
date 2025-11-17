import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function ContactsPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.contacts;
  const org = publicContent[locale].organization;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: org.name,
    url: org.url,
    logo: org.logo,
    sameAs: org.sameAs,
    aggregateRating: org.aggregateRating,
  };

  return (
    <div className="card" data-analytics-id="contacts">
      <SeoHelmet title={seo.title} description={seo.description} path="/contacts" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="grid two">
        <div>
          <h2>{locale === 'uz' ? 'Manzil' : 'Адрес'}</h2>
          <p>Ташкент, ул. Инновационная, 7</p>
          <p>Самарканд, ул. Мирзо Улугбека, 14</p>
        </div>
        <div>
          <h2>{locale === 'uz' ? 'Aloqa' : 'Связаться'}</h2>
          <p>Email: hello@obsidian.dev</p>
          <p>Telegram: @obsidianfreelance</p>
          <p>+998 (90) 123-45-67</p>
        </div>
      </div>
      <section className="card" style={{ marginTop: '2rem' }}>
        <h2>{locale === 'uz' ? 'Ijtimoiy tarmoqlar' : 'Социальные сети'}</h2>
        <ul>
          {org.sameAs.map((link) => (
            <li key={link}>
              <a href={link} target="_blank" rel="noopener noreferrer">
                {link}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
