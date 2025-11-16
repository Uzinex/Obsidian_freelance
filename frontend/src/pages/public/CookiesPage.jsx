import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function CookiesPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.legal.cookies;

  return (
    <div className="card" data-analytics-id="cookies">
      <SeoHelmet title={seo.title} description={seo.description} path="/cookies" noindex jsonLd={{ '@context': 'https://schema.org', '@type': 'WebPage', name: seo.title }} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <p>
        {locale === 'uz'
          ? 'Analitika cookie-lari (GA4, Amplitude) uchun foydalanuvchi roziligi kerak, functional cookie-lar esa xizmat uchun zarur.'
          : 'Для аналитических cookie (GA4, Amplitude) требуется согласие, функциональные cookie обязательны для работы сервиса.'}
      </p>
      <ul>
        <li>{locale === 'uz' ? 'Cookie muddati 12 oy, maʼlumotlar anonim.' : 'Срок хранения cookie — 12 месяцев, данные анонимны.'}</li>
        <li>{locale === 'uz' ? 'Cookie sozlamalarini banner orqali boshqarish mumkin.' : 'Управлять cookie можно через баннер согласия.'}</li>
      </ul>
    </div>
  );
}
