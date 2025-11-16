import { Link } from 'react-router-dom';
import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function BlogIndexPage() {
  const { locale, buildPath } = useLocale();
  const seo = publicContent[locale].seo.blog;
  const articles = publicContent[locale].blog;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Blog',
    name: seo.title,
    blogPost: articles.map((article) => ({
      '@type': 'BlogPosting',
      headline: article.title,
      datePublished: article.publishedAt,
      author: { '@type': 'Person', name: article.author },
    })),
  };

  return (
    <div className="card" data-analytics-id="blog-index">
      <SeoHelmet title={seo.title} description={seo.description} path="/blog" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="grid two">
        {articles.map((article) => (
          <article key={article.slug} className="blog-card">
            <span className="badge">{article.publishedAt}</span>
            <h2>{article.title}</h2>
            <p>{article.description}</p>
            <p className="meta">{article.readingTime}</p>
            <Link to={buildPath(`/blog/${article.slug}`)} className="button ghost">
              {locale === 'uz' ? "O'qish" : 'Читать'}
            </Link>
          </article>
        ))}
      </div>
    </div>
  );
}
