import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function TermsPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.legal.terms;

  return (
    <div className="card" data-analytics-id="terms">
      <SeoHelmet title={seo.title} description={seo.description} path="/terms" noindex jsonLd={{ '@context': 'https://schema.org', '@type': 'WebPage', name: seo.title }} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <p>
        {locale === 'uz'
          ? 'Ushbu shartlar foydalanuvchilarning platformadagi majburiyatlari va to‘lov tartibini belgilaydi.'
          : 'Настоящие условия описывают обязательства пользователей и порядок оплаты услуг платформы.'}
      </p>
      <ul>
        <li>{locale === 'uz' ? 'Escrow bitimlari 48 soat ichida tasdiqlanadi.' : 'Escrow-сделки подтверждаются в течение 48 часов.'}</li>
        <li>
          {locale === 'uz'
            ? 'Talablar va shikoyatlar support@obsidian.dev manziliga yuboriladi.'
            : 'Претензии направляются на support@obsidian.dev.'}
        </li>
      </ul>
    </div>
  );
}
