import { useEffect, useId } from 'react';
import { useLocale } from '../context/LocaleContext.jsx';

const DATA_ATTRIBUTE = 'data-seo-helmet';

function removeByKey(key) {
  if (typeof document === 'undefined') {
    return;
  }
  document.head
    .querySelectorAll(`[${DATA_ATTRIBUTE}="${key}"]`)
    .forEach((node) => node.remove());
}

function manageDocumentTitle(value) {
  if (typeof document === 'undefined') {
    return () => {};
  }
  const previous = document.title;
  document.title = value ?? '';
  return () => {
    document.title = previous;
  };
}

function manageHtmlLang(lang) {
  if (typeof document === 'undefined') {
    return () => {};
  }
  const html = document.documentElement;
  const previous = html.getAttribute('lang');
  if (lang) {
    html.setAttribute('lang', lang);
  } else {
    html.removeAttribute('lang');
  }
  return () => {
    if (previous) {
      html.setAttribute('lang', previous);
    } else {
      html.removeAttribute('lang');
    }
  };
}

function appendHeadTag(tagName, attrs, key, textContent) {
  if (typeof document === 'undefined') {
    return () => {};
  }
  removeByKey(key);
  const element = document.createElement(tagName);
  element.setAttribute(DATA_ATTRIBUTE, key);
  Object.entries(attrs).forEach(([attr, value]) => {
    if (value === null || value === undefined || value === '') {
      return;
    }
    element.setAttribute(attr, value);
  });
  if (textContent !== undefined) {
    element.textContent = textContent;
  }
  document.head.appendChild(element);
  return () => {
    element.remove();
  };
}

function manageMetaByName(name, content, key) {
  if (!content) {
    removeByKey(key);
    return () => {};
  }
  return appendHeadTag(
    'meta',
    {
      name,
      content,
    },
    key,
  );
}

function manageMetaByProperty(property, content, key) {
  if (!content) {
    removeByKey(key);
    return () => {};
  }
  return appendHeadTag(
    'meta',
    {
      property,
      content,
    },
    key,
  );
}

function manageLink(rel, attrs, key) {
  return appendHeadTag(
    'link',
    {
      rel,
      ...attrs,
    },
    key,
  );
}

function manageScript(attrs, key, textContent) {
  return appendHeadTag('script', attrs, key, textContent);
}

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
  const instanceId = useId();

  const ldArray = Array.isArray(jsonLd) ? jsonLd : jsonLd ? [jsonLd] : [];

  useEffect(() => {
    const cleanups = [];
    cleanups.push(manageHtmlLang(localeMeta.langTag));
    if (title) {
      cleanups.push(manageDocumentTitle(title));
    }
    if (description) {
      cleanups.push(manageMetaByName('description', description, `${instanceId}-meta-description`));
    }
    if (noindex) {
      cleanups.push(manageMetaByName('robots', 'noindex,nofollow', `${instanceId}-meta-robots`));
    }
    cleanups.push(manageLink('canonical', { href: canonical }, `${instanceId}-link-canonical`));
    alternateLocales.forEach((alt) => {
      cleanups.push(
        manageLink(
          'alternate',
          {
            hrefLang: alt.locale,
            href: alt.url,
          },
          `${instanceId}-alternate-${alt.locale}`,
        ),
      );
    });
    if (alternateLocales.length > 0) {
      const defaultLocale = alternateLocales[0];
      cleanups.push(
        manageLink(
          'alternate',
          {
            hrefLang: 'x-default',
            href: defaultLocale.url,
          },
          `${instanceId}-alternate-default`,
        ),
      );
    }
    if (title) {
      cleanups.push(manageMetaByProperty('og:title', title, `${instanceId}-og-title`));
      cleanups.push(manageMetaByName('twitter:title', title, `${instanceId}-twitter-title`));
    }
    if (description) {
      cleanups.push(
        manageMetaByProperty('og:description', description, `${instanceId}-og-description`),
      );
      cleanups.push(
        manageMetaByName('twitter:description', description, `${instanceId}-twitter-description`),
      );
    }
    cleanups.push(manageMetaByProperty('og:type', type, `${instanceId}-og-type`));
    cleanups.push(manageMetaByProperty('og:url', canonical, `${instanceId}-og-url`));
    cleanups.push(manageMetaByProperty('og:image', ogImage, `${instanceId}-og-image`));
    cleanups.push(manageMetaByProperty('og:locale', localeMeta.ogLocale, `${instanceId}-og-locale`));
    cleanups.push(
      manageMetaByName('twitter:card', 'summary_large_image', `${instanceId}-twitter-card`),
    );
    cleanups.push(manageMetaByName('twitter:image', ogImage, `${instanceId}-twitter-image`));
    if (localeMeta.twitterHandle) {
      cleanups.push(
        manageMetaByName('twitter:site', localeMeta.twitterHandle, `${instanceId}-twitter-site`),
      );
    }
    ldArray.forEach((schema, index) => {
      cleanups.push(
        manageScript(
          {
            type: 'application/ld+json',
          },
          `${instanceId}-jsonld-${index}`,
          JSON.stringify(schema),
        ),
      );
    });
    return () => {
      cleanups.forEach((dispose) => dispose());
    };
  }, [
    alternateLocales,
    canonical,
    description,
    instanceId,
    ldArray,
    localeMeta.langTag,
    localeMeta.ogLocale,
    localeMeta.twitterHandle,
    noindex,
    ogImage,
    title,
    type,
  ]);

  return null;
}
