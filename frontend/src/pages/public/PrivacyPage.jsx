import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function PrivacyPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.legal.privacy;

  return (
    <div className="card" data-analytics-id="privacy">
      <SeoHelmet title={seo.title} description={seo.description} path="/privacy" noindex jsonLd={{ '@context': 'https://schema.org', '@type': 'PrivacyPolicy', name: seo.title }} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <p>
        {locale === 'uz'
          ? 'Maʼlumotlar Toshkentdagi serverlarda shifrlangan holda saqlanadi, uchinchi shaxslarga sotilmaydi.'
          : 'Данные хранятся на серверах в Ташкенте, шифруются и не продаются третьим лицам.'}
      </p>
      <ul>
        <li>{locale === 'uz' ? 'User maʼlumotlari talab bo‘yicha 30 kun ichida o‘chiriladi.' : 'Персональные данные удаляются по запросу за 30 дней.'}</li>
        <li>{locale === 'uz' ? 'GDPR va UzInfoCom talablariga moslikni audit qilamiz.' : 'Соблюдаем GDPR и требования UzInfoCom.'}</li>
      </ul>
    </div>
  );
}
