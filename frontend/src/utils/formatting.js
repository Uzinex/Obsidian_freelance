import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import localizedFormat from 'dayjs/plugin/localizedFormat';

dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(localizedFormat);

export const TASHKENT_TIMEZONE = 'Asia/Tashkent';
dayjs.tz.setDefault(TASHKENT_TIMEZONE);

const SUPPORTED_LOCALES = ['ru', 'uz'];
const FALLBACK_LOCALES = ['ru', 'uz'];
const NUMBER_LOCALE_MAP = {
  ru: 'ru-RU',
  uz: 'uz-UZ',
};

const CURRENCY_LABELS = {
  ru: { UZS: 'сум' },
  uz: { UZS: "so'm" },
};

const numberFormatters = new Map();
const pluralRulesCache = new Map();

export function resolveLocale(inputLocale) {
  const normalized = (inputLocale || '').toLowerCase();
  const directMatch = SUPPORTED_LOCALES.find((locale) => normalized.startsWith(locale));
  if (directMatch) {
    return directMatch;
  }
  return FALLBACK_LOCALES[0];
}

function getNumberFormatter(locale, options) {
  const intlLocale = NUMBER_LOCALE_MAP[locale] ?? NUMBER_LOCALE_MAP.ru;
  const key = JSON.stringify({ locale: intlLocale, ...options });
  if (!numberFormatters.has(key)) {
    numberFormatters.set(key, new Intl.NumberFormat(intlLocale, options));
  }
  return numberFormatters.get(key);
}

export function formatNumber(value, { locale, minimumFractionDigits = 0, maximumFractionDigits = 2 } = {}) {
  if (value === null || value === undefined || value === '') {
    return '';
  }
  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }
  const normalized = resolveLocale(locale);
  const formatter = getNumberFormatter(normalized, {
    minimumFractionDigits,
    maximumFractionDigits,
  });
  return formatter.format(numeric);
}

export function formatCurrency(
  amount,
  { currency = 'UZS', locale, minimumFractionDigits, maximumFractionDigits } = {},
) {
  if (amount === null || amount === undefined || amount === '') {
    return '';
  }
  const normalized = resolveLocale(locale);
  const digits = currency === 'UZS' ? 0 : 2;
  const formattedNumber = formatNumber(amount, {
    locale: normalized,
    minimumFractionDigits: minimumFractionDigits ?? digits,
    maximumFractionDigits: maximumFractionDigits ?? digits,
  });
  const label = CURRENCY_LABELS[normalized]?.[currency] ?? currency;
  return `${formattedNumber} ${label}`.trim();
}

function normalizeDateInput(value) {
  const date = dayjs(value);
  return date.isValid() ? date.tz(TASHKENT_TIMEZONE) : null;
}

export function formatDate(value, { locale, pattern } = {}) {
  const date = normalizeDateInput(value);
  if (!date) {
    return '';
  }
  const fmt = pattern ?? 'DD.MM.YYYY';
  resolveLocale(locale); // keep interface symmetrical for future overrides
  return date.format(fmt);
}

export function formatDateTime(value, { locale, pattern } = {}) {
  const date = normalizeDateInput(value);
  if (!date) {
    return '';
  }
  const fmt = pattern ?? 'DD.MM.YYYY HH:mm';
  resolveLocale(locale);
  return date.format(fmt);
}

const RELATIVE_COPY = {
  ru: {
    today: 'сегодня',
    yesterday: 'вчера',
    tomorrow: 'завтра',
    past: '{count} {unit} назад',
    future: 'через {count} {unit}',
    dayForms: { one: 'день', few: 'дня', many: 'дней', other: 'дня' },
  },
  uz: {
    today: 'bugun',
    yesterday: 'kecha',
    tomorrow: 'ertaga',
    past: '{count} {unit} oldin',
    future: "yana {count} {unit} ichida",
    dayForms: { one: 'kun', other: 'kun' },
  },
};

export function formatPlural(count, locale, forms) {
  const normalized = resolveLocale(locale);
  if (!pluralRulesCache.has(normalized)) {
    pluralRulesCache.set(normalized, new Intl.PluralRules(normalized));
  }
  const rule = pluralRulesCache.get(normalized);
  const category = rule.select(Math.abs(Number(count)) || 0);
  return forms[category] ?? forms.other ?? forms.one ?? '';
}

export function formatRelativeDate(value, { locale, thresholdDays = 7 } = {}) {
  const date = normalizeDateInput(value);
  if (!date) {
    return '';
  }
  const normalized = resolveLocale(locale);
  const copy = RELATIVE_COPY[normalized] ?? RELATIVE_COPY.ru;
  const today = dayjs().tz(TASHKENT_TIMEZONE).startOf('day');
  const target = date.startOf('day');
  const diffDays = target.diff(today, 'day');
  if (diffDays === 0) {
    return copy.today;
  }
  if (diffDays === -1) {
    return copy.yesterday;
  }
  if (diffDays === 1) {
    return copy.tomorrow;
  }
  if (Math.abs(diffDays) > thresholdDays) {
    return date.format('DD.MM.YYYY');
  }
  const unit = formatPlural(Math.abs(diffDays), normalized, copy.dayForms);
  const template = diffDays > 0 ? copy.future : copy.past;
  return template.replace('{count}', Math.abs(diffDays)).replace('{unit}', unit);
}
