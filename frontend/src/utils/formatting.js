export const TASHKENT_TIMEZONE = 'Asia/Tashkent';
const DAY_IN_MS = 24 * 60 * 60 * 1000;

const tzFormatter = new Intl.DateTimeFormat('en-CA', {
  timeZone: TASHKENT_TIMEZONE,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

function parseDate(value) {
  if (value instanceof Date) {
    const cloned = new Date(value.getTime());
    return Number.isNaN(cloned.getTime()) ? null : cloned;
  }
  const date = new Date(value ?? '');
  return Number.isNaN(date.getTime()) ? null : date;
}

function extractParts(date) {
  const parts = { year: 0, month: 0, day: 0, hour: 0, minute: 0 };
  tzFormatter.formatToParts(date).forEach(({ type, value }) => {
    if (type in parts) {
      parts[type] = Number(value);
    }
  });
  const startOfDay = Date.UTC(parts.year, parts.month - 1, parts.day);
  const timestamp = Date.UTC(
    parts.year,
    parts.month - 1,
    parts.day,
    parts.hour,
    parts.minute,
  );
  return { ...parts, startOfDay, timestamp };
}

function getZonedDate(value) {
  const date = parseDate(value);
  if (!date) {
    return null;
  }
  return extractParts(date);
}

function formatPattern(parts, pattern) {
  const replacements = {
    DD: String(parts.day).padStart(2, '0'),
    MM: String(parts.month).padStart(2, '0'),
    YYYY: String(parts.year).padStart(4, '0'),
    HH: String(parts.hour).padStart(2, '0'),
    mm: String(parts.minute).padStart(2, '0'),
  };
  return pattern.replace(/YYYY|DD|MM|HH|mm/g, (token) => replacements[token] ?? token);
}

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

export function formatDate(value, { locale, pattern } = {}) {
  const zoned = getZonedDate(value);
  if (!zoned) {
    return '';
  }
  const fmt = pattern ?? 'DD.MM.YYYY';
  resolveLocale(locale); // keep interface symmetrical for future overrides
  return formatPattern(zoned, fmt);
}

export function formatDateTime(value, { locale, pattern } = {}) {
  const zoned = getZonedDate(value);
  if (!zoned) {
    return '';
  }
  const fmt = pattern ?? 'DD.MM.YYYY HH:mm';
  resolveLocale(locale);
  return formatPattern(zoned, fmt);
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
  const zoned = getZonedDate(value);
  if (!zoned) {
    return '';
  }
  const normalized = resolveLocale(locale);
  const copy = RELATIVE_COPY[normalized] ?? RELATIVE_COPY.ru;
  const today = getZonedDate(new Date());
  const diffDays = Math.round((zoned.startOfDay - today.startOfDay) / DAY_IN_MS);
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
    return formatPattern(zoned, 'DD.MM.YYYY');
  }
  const unit = formatPlural(Math.abs(diffDays), normalized, copy.dayForms);
  const template = diffDays > 0 ? copy.future : copy.past;
  return template.replace('{count}', Math.abs(diffDays)).replace('{unit}', unit);
}
