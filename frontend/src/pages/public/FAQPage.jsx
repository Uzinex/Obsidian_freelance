import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function FAQPage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.faq;
  const faqs = publicContent[locale].faq;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: { '@type': 'Answer', text: item.answer },
    })),
  };

  return (
    <div className="card" data-analytics-id="faq">
      <SeoHelmet title={seo.title} description={seo.description} path="/faq" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="accordion">
        {faqs.map((item) => (
          <details key={item.question} open>
            <summary>{item.question}</summary>
            <p>{item.answer}</p>
          </details>
        ))}
      </div>
    </div>
  );
}
