import { createContext, useContext, useMemo } from 'react';
import { useLocation, useParams } from 'react-router-dom';

const SUPPORTED_LOCALES = ['ru', 'uz'];
const DEFAULT_LOCALE = 'ru';
const SITE_URL = 'https://obsidianfreelance.com';

const LOCALE_META = {
  ru: {
    label: 'Русский',
    langTag: 'ru-RU',
    ogLocale: 'ru_RU',
    twitterHandle: '@obsidian_ru',
  },
  uz: {
    label: "O'zbekcha",
    langTag: 'uz-UZ',
    ogLocale: 'uz_UZ',
    twitterHandle: '@obsidian_uz',
  },
};

const LocaleContext = createContext(null);

function normalizePath(path) {
  if (!path || path === '/') {
    return '/';
  }
  return path.startsWith('/') ? path : `/${path}`;
}

function buildLocalizedPath(targetPath, locale) {
  const normalized = normalizePath(targetPath ?? '/');
  const suffix = normalized === '/' ? '' : normalized;
  const path = `/${locale}${suffix}`;
  return path === `/${locale}` ? `/${locale}` : path;
}

export function LocaleProvider({ children }) {
  const location = useLocation();
  const params = useParams();

  const localeFromPath = params?.locale;
  const isLocaleSegment = SUPPORTED_LOCALES.includes(localeFromPath);
  const locale = isLocaleSegment ? localeFromPath : DEFAULT_LOCALE;

  const pathSegments = location.pathname.split('/').filter(Boolean);
  const pathWithoutLocale = (() => {
    if (!isLocaleSegment) {
      return normalizePath(location.pathname) || '/';
    }
    const restSegments = pathSegments.slice(1);
    if (restSegments.length === 0) {
      return '/';
    }
    return `/${restSegments.join('/')}`;
  })();

  const buildPath = (targetPath = '/', localeOverride) =>
    buildLocalizedPath(targetPath, localeOverride || locale);

  const buildAbsoluteUrl = (targetPath = '/', localeOverride) => {
    return `${SITE_URL}${buildPath(targetPath, localeOverride)}`;
  };

  const canonicalUrl = buildAbsoluteUrl(pathWithoutLocale, locale);
  const alternateLocales = SUPPORTED_LOCALES.map((loc) => ({
    locale: loc,
    langTag: LOCALE_META[loc].langTag,
    url: buildAbsoluteUrl(pathWithoutLocale, loc),
  }));

  const value = useMemo(
    () => ({
      locale,
      defaultLocale: DEFAULT_LOCALE,
      localeMeta: LOCALE_META[locale],
      siteUrl: SITE_URL,
      pathWithoutLocale,
      buildPath,
      buildAbsoluteUrl,
      canonicalUrl,
      alternateLocales,
      languageTag: LOCALE_META[locale].langTag,
    }),
    [locale, pathWithoutLocale, canonicalUrl],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error('useLocale must be used within LocaleProvider');
  }
  return ctx;
}
