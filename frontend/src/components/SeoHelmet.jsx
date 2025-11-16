import { Helmet } from 'react-helmet-async';
import { useLocale } from '../context/LocaleContext.jsx';

export default function SeoHelmet({
  title,
  description,
  path = '/',
  ogImage = 'https://cdn.obsidianfreelance.com/meta/og-default.png',
  type = 'website',
  noindex = false,
  jsonLd,
}) {
  const { buildAbsoluteUrl, alternateLocales, localeMeta } = useLocale();
  const canonical = buildAbsoluteUrl(path);

  const ldArray = Array.isArray(jsonLd) ? jsonLd : jsonLd ? [jsonLd] : [];

  return (
    <Helmet>
      <html lang={localeMeta.langTag} />
      <title>{title}</title>
      <meta name="description" content={description} />
      {noindex ? <meta name="robots" content="noindex,nofollow" /> : null}
      <link rel="canonical" href={canonical} />
      {alternateLocales.map((alt) => (
        <link key={alt.locale} rel="alternate" hrefLang={alt.locale} href={alt.url} />
      ))}
      {alternateLocales.length > 0 ? (
        <link rel="alternate" hrefLang="x-default" href={alternateLocales[0].url} />
      ) : null}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content={type} />
      <meta property="og:url" content={canonical} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:locale" content={localeMeta.ogLocale} />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />
      <meta name="twitter:site" content={localeMeta.twitterHandle} />
      {ldArray.map((schema, index) => (
        <script key={index} type="application/ld+json">
          {JSON.stringify(schema)}
        </script>
      ))}
    </Helmet>
  );
}
