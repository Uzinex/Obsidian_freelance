import { useEffect, useMemo, useState } from 'react';
import { resolveLocale } from '../utils/formatting.js';

const STORAGE_KEY = 'obsidian_cookie_preferences_v1';
const CONSENT_VERSION = '2024-12-01';

const COPY = {
  ru: {
    title: 'Мы используем cookie',
    description:
      'Строго необходимые cookie помогают обеспечить безопасность сессий. Вы можете отдельно разрешить аналитику и маркетинг.',
    actions: {
      acceptAll: 'Принять все',
      save: 'Сохранить выбор',
      preferences: 'Настроить',
    },
    categories: {
      necessary: {
        label: 'Строго необходимые',
        description: 'Сессии, безопасность, запоминание языка. Всегда активны.',
      },
      analytics: {
        label: 'Аналитика',
        description: 'Помогают измерять продуктовые метрики и обнаруживать ошибки.',
      },
      marketing: {
        label: 'Маркетинг',
        description: 'Показываем релевантные предложения и партнёрские кампании.',
      },
    },
    links: {
      terms: 'Условия',
      privacy: 'Политика конфиденциальности',
      cookies: 'Политика cookie',
      aml: 'AML/KYC уведомление',
    },
  },
  uz: {
    title: 'Biz cookie fayllaridan foydalanamiz',
    description:
      'Majburiy cookie sessiyalarni va xavfsizlikni taʼminlaydi. Analitika va marketingni alohida yoqishingiz mumkin.',
    actions: {
      acceptAll: 'Hammasini qabul qilish',
      save: 'Tanlovni saqlash',
      preferences: 'Moslashtirish',
    },
    categories: {
      necessary: {
        label: 'Majburiy',
        description: 'Sessiyalar, xavfsizlik, tilni eslab qolish. Doimo faol.',
      },
      analytics: {
        label: 'Analitika',
        description: 'Mahsulot metrikalari va xatolarni aniqlashga yordam beradi.',
      },
      marketing: {
        label: 'Marketing',
        description: 'Mos keladigan takliflar va hamkorlikdagi kampaniyalar.',
      },
    },
    links: {
      terms: 'Foydalanish shartlari',
      privacy: 'Maxfiylik siyosati',
      cookies: 'Cookie siyosati',
      aml: 'AML/KYC xabarnomasi',
    },
  },
};

const defaultConsent = {
  necessary: true,
  analytics: false,
  marketing: false,
};

function syncTrackingConsent(consent) {
  if (typeof window === 'undefined') {
    return;
  }
  const payload = { ...consent, version: CONSENT_VERSION, updated_at: new Date().toISOString() };
  if (window.dataLayer) {
    window.dataLayer.push({ event: 'cookie_consent_updated', consent: payload });
  }
  if (window.obsidianTracking?.setConsent) {
    window.obsidianTracking.setConsent(payload);
  }
}

function persistConsent(consent) {
  try {
    const payload = { ...consent, version: CONSENT_VERSION, saved_at: new Date().toISOString() };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    return payload;
  } catch (error) {
    console.warn('Не удалось сохранить cookie-настройки', error);
    return null;
  }
}

function loadConsent() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (parsed.version !== CONSENT_VERSION) {
      return null;
    }
    return parsed;
  } catch (error) {
    console.warn('Не удалось прочитать cookie-настройки', error);
    return null;
  }
}

export default function CookieConsentBanner() {
  const [preferences, setPreferences] = useState(defaultConsent);
  const [isVisible, setIsVisible] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const locale = useMemo(() => resolveLocale(typeof navigator !== 'undefined' ? navigator.language : 'ru'), []);
  const copy = COPY[locale] || COPY.ru;

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const saved = loadConsent();
    if (saved) {
      setPreferences({
        necessary: true,
        analytics: Boolean(saved.analytics),
        marketing: Boolean(saved.marketing),
      });
      setIsVisible(false);
      syncTrackingConsent(saved);
      return;
    }
    setIsVisible(true);
  }, []);

  useEffect(() => {
    if (!isVisible) {
      syncTrackingConsent({ ...preferences, necessary: true });
    }
  }, [isVisible, preferences]);

  if (!isVisible) {
    return null;
  }

  const handleToggle = (name) => {
    if (name === 'necessary') return;
    setPreferences((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  const handleAcceptAll = () => {
    const payload = { necessary: true, analytics: true, marketing: true };
    setPreferences(payload);
    persistConsent(payload);
    setIsVisible(false);
  };

  const handleSave = () => {
    persistConsent(preferences);
    setIsVisible(false);
  };

  return (
    <div className="cookie-banner" role="dialog" aria-live="polite">
      <div className="cookie-banner__content">
        <div>
          <h3>{copy.title}</h3>
          <p>{copy.description}</p>
          <p className="cookie-banner__links">
            <a href="/legal/terms" target="_blank" rel="noreferrer">
              {copy.links.terms}
            </a>
            <span aria-hidden="true">·</span>
            <a href="/legal/privacy" target="_blank" rel="noreferrer">
              {copy.links.privacy}
            </a>
            <span aria-hidden="true">·</span>
            <a href="/legal/cookies" target="_blank" rel="noreferrer">
              {copy.links.cookies}
            </a>
            <span aria-hidden="true">·</span>
            <a href="/legal/aml-kyc" target="_blank" rel="noreferrer">
              {copy.links.aml}
            </a>
          </p>
        </div>
        <button className="button ghost" type="button" onClick={() => setExpanded((prev) => !prev)}>
          {copy.actions.preferences}
        </button>
      </div>
      {expanded && (
        <div className="cookie-banner__preferences">
          {Object.entries(copy.categories).map(([key, category]) => (
            <label key={key} className={`cookie-pref cookie-pref--${key}`}>
              <span>
                <strong>{category.label}</strong>
                <small>{category.description}</small>
              </span>
              <input
                type="checkbox"
                checked={preferences[key]}
                onChange={() => handleToggle(key)}
                disabled={key === 'necessary'}
              />
            </label>
          ))}
        </div>
      )}
      <div className="cookie-banner__actions">
        <button className="button secondary" type="button" onClick={handleSave}>
          {copy.actions.save}
        </button>
        <button className="button primary" type="button" onClick={handleAcceptAll}>
          {copy.actions.acceptAll}
        </button>
      </div>
    </div>
  );
}
