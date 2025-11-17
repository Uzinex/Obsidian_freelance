import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';
import Icon from '../../components/Icon.jsx';

function formatTierPrice(tier, locale) {
  if (tier.price === 'custom') {
    return locale === 'uz' ? 'Individual' : 'Индивидуально';
  }
  if (tier.currency === 'budget_share') {
    return `${tier.price * 100}% бюджета`;
  }
  if (typeof tier.price === 'number') {
    const formatter = new Intl.NumberFormat(locale === 'uz' ? 'uz-UZ' : 'ru-RU');
    const label = locale === 'uz' ? "so'm" : 'сум';
    return `${formatter.format(tier.price)} ${tier.currency === 'UZS' ? label : tier.currency}`;
  }
  return tier.price;
}

export default function PricingPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.pricing;
  const { tiers, payouts, changelog, offers } = publicContent[locale].pricing;
  const organization = publicContent[locale].organization;

  const jsonLd = [
    {
      '@context': 'https://schema.org',
      '@type': 'Service',
      name: seo.title,
      provider: { '@type': 'Organization', name: organization.name, url: organization.url },
      offers,
    },
    {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: locale === 'uz' ? 'Escrow yangilanishlari' : 'Escrow changelog',
    },
  ];

  return (
    <div className="pricing-page">
      <SeoHelmet title={seo.title} description={seo.description} path="/pricing" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="pricing-grid">
        {tiers.map((tier) => (
          <article key={tier.name} className="pricing-tier">
            <div className="pricing-tier-head">
              <h2>{tier.name}</h2>
              <p>{tier.description}</p>
              <span className="price-tag">{formatTierPrice(tier, locale)}</span>
            </div>
            <ul>
              {tier.features.map((feature) => (
                <li key={feature}>
                  <Icon name="check" size={16} decorative /> {feature}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
      <section className="card payouts">
        <h2>{locale === 'uz' ? 'To‘lov kanallari' : 'Пополнение и выплаты'}</h2>
        <ul>
          {payouts.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      <section className="card changelog">
        <h2>{locale === 'uz' ? 'Escrow yangilanishlari' : 'Публичный changelog escrow'}</h2>
        <div className="changelog-list">
          {changelog.map((entry) => (
            <article key={entry.version} className="changelog-entry">
              <header>
                <strong>{entry.version}</strong>
                <span>{entry.date}</span>
              </header>
              <p>{entry.summary}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
