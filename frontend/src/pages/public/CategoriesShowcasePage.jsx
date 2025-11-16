import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

export default function CategoriesShowcasePage() {
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.categories;
  const categories = publicContent[locale].categories;
  const skills = publicContent[locale].skills;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: seo.title,
    itemListElement: categories.map((category, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: category.name,
      description: category.description,
    })),
  };

  return (
    <div className="card" data-analytics-id="categories">
      <SeoHelmet title={seo.title} description={seo.description} path="/categories" jsonLd={jsonLd} />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="grid two">
        {categories.map((category) => (
          <article key={category.slug} className="category-card">
            <h2>{category.name}</h2>
            <p>{category.description}</p>
          </article>
        ))}
      </div>
      <section className="card" style={{ marginTop: '2rem' }}>
        <h2>{locale === 'uz' ? 'Top skills' : 'Ключевые навыки'}</h2>
        <div className="skill-pills">
          {skills.map((skill) => (
            <span key={skill} className="skill-pill">
              {skill}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}
