import { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { findArticleBySlug, publicContent } from '../../mocks/publicContent.js';

export default function BlogArticlePage() {
  const { locale } = useLocale();
  const { slug } = useParams();
  const article = useMemo(() => findArticleBySlug(locale, slug) ?? publicContent[locale].blog[0], [locale, slug]);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    datePublished: article.publishedAt,
    author: { '@type': 'Person', name: article.author },
    image: article.cover,
    articleSection: article.tags,
    description: article.description,
  };

  return (
    <div className="card" data-analytics-id="blog-article">
      <SeoHelmet title={article.title} description={article.description} path={`/blog/${article.slug}`} ogImage={article.cover} jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <span className="badge">{article.publishedAt}</span>
          <h1>{article.title}</h1>
          <p>{article.description}</p>
        </div>
      </header>
      {article.body.map((paragraph) => (
        <p key={paragraph}>{paragraph}</p>
      ))}
    </div>
  );
}
