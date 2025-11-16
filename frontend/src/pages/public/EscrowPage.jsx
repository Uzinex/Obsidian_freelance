import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';
import { trackEvent } from '../../utils/analytics.js';

const escrowFeatures = {
  ru: [
    {
      title: 'Бюджет под защитой',
      description: 'Деньги хранятся на сегрегированном счёте банка-партнёра и разблокируются после приёмки.',
    },
    {
      title: 'Staged-платежи',
      description: 'Каждый спринт имеет свой лимит, SLA и webhooks для автоматизации.',
    },
    {
      title: 'Панель прозрачности',
      description: 'Владелец проекта видит burn-down, финансовые потоки и логи доступов.',
    },
  ],
  uz: [
    {
      title: 'Budjet himoyada',
      description: 'Pul sherik bank hisobida saqlanadi va qabuldan keyin yechiladi.',
    },
    {
      title: 'Bosqichma-bosqich to‘lov',
      description: 'Har bir sprintga alohida limit va SLA belgilanadi.',
    },
    {
      title: 'Shaffof panel',
      description: 'Buyurtmachi burn-down va moliyaviy loglarni ko‘radi.',
    },
  ],
};

export default function EscrowPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.escrow;
  const features = escrowFeatures[locale];
  const reviews = publicContent[locale].reviews;

  const reviewLd = reviews.map((review) => ({
    '@type': 'Review',
    author: review.author,
    reviewBody: review.review,
    reviewRating: { '@type': 'Rating', ratingValue: review.rating },
  }));

  const aggregateLd = {
    '@type': 'AggregateRating',
    ratingValue: publicContent[locale].organization.aggregateRating.ratingValue,
    reviewCount: publicContent[locale].organization.aggregateRating.reviewCount,
  };

  return (
    <div className="card" data-analytics-id="escrow">
      <SeoHelmet
        title={seo.title}
        description={seo.description}
        path="/escrow"
        jsonLd={{ '@context': 'https://schema.org', '@type': 'Service', name: seo.title, aggregateRating: aggregateLd, review: reviewLd }}
      />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="grid three">
        {features.map((feature) => (
          <article
            key={feature.title}
            className="feature-card"
            role="button"
            tabIndex={0}
            onClick={() => trackEvent('escrow_benefit_click', { locale, feature: feature.title })}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                trackEvent('escrow_benefit_click', { locale, feature: feature.title });
              }
            }}
          >
            <h2>{feature.title}</h2>
            <p>{feature.description}</p>
          </article>
        ))}
      </div>
      <section className="card" style={{ marginTop: '2rem' }}>
        <h2>{locale === 'uz' ? 'Escrow afzalliklari' : 'Преимущества escrow'}</h2>
        <ul>
          <li>
            {locale === 'uz'
              ? 'AML/KYC tekshiruvi va avtomatik compliance loglar.'
              : 'AML/KYC проверка и автоматические compliance-логи.'}
          </li>
          <li>{locale === 'uz' ? 'Stale-while-revalidate bilan real vaqt rejimida status.' : 'Стратегия stale-while-revalidate для статусов в реальном времени.'}</li>
          <li>
            {locale === 'uz'
              ? 'Grafana va Looker Studio dashboardlaridan konversiyani kuzatish.'
              : 'Наблюдаемость в Grafana и Looker Studio для анализа конверсии.'}
          </li>
        </ul>
      </section>
    </div>
  );
}
