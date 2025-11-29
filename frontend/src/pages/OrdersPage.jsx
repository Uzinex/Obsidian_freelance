import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { fetchCategories, fetchOrders, fetchSkills } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import { formatCurrency, formatDate } from '../utils/formatting.js';
import SeoHelmet from '../components/SeoHelmet.jsx';
import { publicContent } from '../mocks/publicContent.js';
import Icon from '../components/Icon.jsx';

const orderTypeLabels = {
  urgent: 'Срочный',
  non_urgent: 'Несрочный',
  premium: 'Премиум',
  standard: 'Стандартный',
  company_only: 'Только компании',
  individual_only: 'Только фрилансеры',
};

const FILTER_STORAGE_KEY = 'obsidian.orders.filters';
const SAVED_FILTERS_KEY = 'obsidian.orders.savedFilters';
const SUBSCRIPTION_STORAGE_KEY = 'obsidian.orders.subscription';

const SUBSCRIPTION_DEFAULT = { email: '', telegram: '', channel: 'email' };

function toObject(params) {
  return Object.fromEntries(params.entries());
}

function serializeParams(object) {
  const sortedEntries = Object.entries(object).sort(([a], [b]) => a.localeCompare(b));
  return new URLSearchParams(sortedEntries).toString();
}

export default function OrdersPage() {
  const [params, setParams] = useSearchParams();
  const [orders, setOrders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [debouncedQuery, setDebouncedQuery] = useState(() => toObject(params));
  const [debouncedQueryKey, setDebouncedQueryKey] = useState(() =>
    serializeParams(toObject(params)),
  );
  const [savedFilters, setSavedFilters] = useState([]);
  const [saveLabel, setSaveLabel] = useState('');
  const [subscription, setSubscription] = useState(SUBSCRIPTION_DEFAULT);
  const [subscriptionStatus, setSubscriptionStatus] = useState('');
  const [quickApplyMessages, setQuickApplyMessages] = useState({});
  const [quickApplyStatus, setQuickApplyStatus] = useState({});
  const { isAuthenticated, user } = useAuth();
  const { locale, buildPath, buildAbsoluteUrl } = useLocale();
  const seo = publicContent[locale].seo.orders;

  const role = user?.profile?.role || user?.role;
  const paramsKey = params.toString();
  const filtersLoadedRef = useRef(false);

  useEffect(() => {
    async function loadFilters() {
      try {
        const [categoryData, skillData] = await Promise.all([
          fetchCategories(),
          fetchSkills(),
        ]);
        setCategories(categoryData.results || categoryData);
        setSkills(skillData.results || skillData);
      } catch (error) {
        console.error('Не удалось загрузить фильтры', error);
      }
    }
    if (!filtersLoadedRef.current) {
      filtersLoadedRef.current = true;
      loadFilters();
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let isMounted = true;

    async function loadOrders() {
      setLoading(true);
      try {
        const data = await fetchOrders(debouncedQuery, { signal: controller.signal });
        if (isMounted) {
          setOrders(data.results || data);
        }
      } catch (error) {
        if (!controller.signal.aborted && error.name !== 'CanceledError' && error.name !== 'AbortError') {
          console.error('Не удалось загрузить заказы', error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadOrders();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [debouncedQuery, debouncedQueryKey]);

  useEffect(() => {
    const nextQuery = toObject(params);
    const nextQueryKey = serializeParams(nextQuery);
    if (nextQueryKey === debouncedQueryKey) {
      return undefined;
    }
    const timeout = setTimeout(() => {
      setDebouncedQuery(nextQuery);
      setDebouncedQueryKey(nextQueryKey);
    }, 250);

    return () => {
      clearTimeout(timeout);
    };
  }, [debouncedQueryKey, paramsKey]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const storedFilters = window.localStorage.getItem(FILTER_STORAGE_KEY);
    const storedSavedFilters = window.localStorage.getItem(SAVED_FILTERS_KEY);
    const storedSubscription = window.localStorage.getItem(SUBSCRIPTION_STORAGE_KEY);

    if (storedFilters) {
      try {
        const parsed = JSON.parse(storedFilters);
        if (parsed && typeof parsed === 'object') {
          setParams(new URLSearchParams(parsed), { replace: true });
        }
      } catch (error) {
        console.warn('Не удалось восстановить фильтры заказов', error);
      }
    }

    if (storedSavedFilters) {
      try {
        setSavedFilters(JSON.parse(storedSavedFilters) || []);
      } catch (error) {
        console.warn('Не удалось восстановить сохранённые фильтры', error);
      }
    }

    if (storedSubscription) {
      try {
        setSubscription(JSON.parse(storedSubscription));
      } catch (error) {
        console.warn('Не удалось восстановить настройки подписки', error);
      }
    }
  }, [setParams]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    window.localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(toObject(params)));
  }, [paramsKey]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const currentValue = params.get(name) || '';
    const nextValue = typeof value === 'string' ? value : String(value ?? '');

    if (currentValue === nextValue) {
      return;
    }

    const next = new URLSearchParams(params);
    if (nextValue) {
      next.set(name, nextValue);
    } else {
      next.delete(name);
    }
    setParams(next, { replace: true });
  };

  const handleClearFilters = () => {
    setParams(new URLSearchParams());
  };

  const handleSaveCurrentFilters = (event) => {
    event.preventDefault();
    const label = saveLabel.trim();
    if (!label) {
      return;
    }
    const snapshot = toObject(params);
    const existing = savedFilters.filter((item) => item.label !== label);
    const next = [...existing, { label, values: snapshot }];
    setSavedFilters(next);
    setSaveLabel('');
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(next));
    }
  };

  const handleApplySavedFilter = (filter) => {
    setParams(new URLSearchParams(filter.values));
  };

  const handleDeleteSavedFilter = (label) => {
    const next = savedFilters.filter((item) => item.label !== label);
    setSavedFilters(next);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(next));
    }
  };

  const handleSubscriptionChange = (event) => {
    const { name, value } = event.target;
    setSubscription((prev) => ({ ...prev, [name]: value }));
  };

  const handleChannelChange = (event) => {
    setSubscription((prev) => ({ ...prev, channel: event.target.value }));
  };

  const handleSubscribe = (event) => {
    event.preventDefault();
    setSubscriptionStatus('pending');
    const snapshot = { ...subscription };
    setTimeout(() => {
      setSubscriptionStatus('success');
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(SUBSCRIPTION_STORAGE_KEY, JSON.stringify(snapshot));
      }
    }, 500);
  };

  const handleQuickApplyChange = (orderId, value) => {
    setQuickApplyMessages((prev) => ({ ...prev, [orderId]: value }));
  };

  const handleQuickApplySubmit = (orderId) => {
    setQuickApplyStatus((prev) => ({ ...prev, [orderId]: 'pending' }));
    setTimeout(() => {
      setQuickApplyStatus((prev) => ({ ...prev, [orderId]: 'sent' }));
    }, 600);
  };

  const ordersFaq = useMemo(() => {
    if (locale === 'uz') {
      return [
        {
          question: 'Buyurtmalar qanchalik tez yangilanadi?',
          answer:
            'Platforma har 2 soatda yangi briflarni tekshiradi va moderatsiyadan o‘tkazadi. Premium buyurtmalar push orqali birinchi bo‘lib keladi.',
        },
        {
          question: 'Filtrlarni saqlash va ularga qaytish mumkinmi?',
          answer:
            'Ha, “Saqlangan filtrlar” bo‘limida kerakli kombinatsiyani nom bilan yozib qo‘ying va bir marta bosishda ishga tushiring.',
        },
      ];
    }
    return [
      {
        question: 'Как часто обновляются заказы?',
        answer:
          'Модераторы публикуют новые заявки каждые 2 часа, а заявки уровня premium появляются в push-уведомлениях моментально.',
      },
      {
        question: 'Можно ли сохранить фильтры и вернуться к ним позже?',
        answer:
          'Да, используйте блок «Сохранённые фильтры»: задайте название подборки и применяйте её одним кликом на любой странице.',
      },
    ];
  }, [locale]);

  const breadcrumbLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        {
          '@type': 'ListItem',
          position: 1,
          name: 'Главная',
          item: buildAbsoluteUrl('/'),
        },
        {
          '@type': 'ListItem',
          position: 2,
          name: seo.title,
          item: buildAbsoluteUrl('/orders'),
        },
      ],
    }),
    [buildAbsoluteUrl, seo.title],
  );

  const itemListLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      itemListElement: orders.slice(0, 10).map((order, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        url: buildAbsoluteUrl(`/orders/${order.id}`),
        name: order.title,
      })),
    }),
    [orders, buildAbsoluteUrl],
  );

  const faqLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: ordersFaq.map((faq) => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    }),
    [ordersFaq],
  );

  const jobPostingLd = useMemo(
    () =>
      orders.slice(0, 5).map((order) => {
        const skillsList = order.required_skill_details?.map((skill) => skill.name).filter(Boolean);
        const salary =
          order.budget && order.currency
            ? {
                '@type': 'MonetaryAmount',
                currency: order.currency,
                value: {
                  '@type': 'QuantitativeValue',
                  value: Number(order.budget),
                },
              }
            : undefined;
        return {
          '@context': 'https://schema.org',
          '@type': 'JobPosting',
          title: order.title,
          description: order.description,
          datePosted: order.created_at,
          validThrough: order.deadline,
          employmentType: order.order_type,
          hiringOrganization: {
            '@type': 'Organization',
            name: publicContent[locale].organization.name,
            sameAs: publicContent[locale].organization.sameAs,
          },
          jobLocationType: 'TELECOMMUTE',
          jobLocation: {
            '@type': 'Place',
            address: {
              '@type': 'PostalAddress',
              addressCountry: 'UZ',
            },
          },
          skills: skillsList,
          baseSalary: salary,
          identifier: order.id,
          workHours: order.payment_type === 'hourly' ? 'hourly' : 'project',
        };
      }),
    [orders, locale],
  );

  const jsonLd = useMemo(() => [breadcrumbLd, itemListLd, faqLd, ...jobPostingLd], [
    breadcrumbLd,
    itemListLd,
    faqLd,
    jobPostingLd,
  ]);

  return (
    <div className="orders-page">
      <SeoHelmet title={seo.title} description={seo.description} path="/orders" jsonLd={jsonLd} />
      <section className="card soft page-header">
        <div className="page-header-content">
          <span className="page-header-icon">
            <Icon name="orders" size={28} decorative />
          </span>
          <div>
            <h1>{seo.title}</h1>
            <p>{seo.description}</p>
          </div>
        </div>
        {role === 'client' && isAuthenticated && (
          <Link to={buildPath('/orders/create')} className="button primary">
            Создать заказ
          </Link>
        )}
      </section>

      <section className="card filter-card">
        <div className="filter-card-header">
          <div>
            <h2>Подбор параметров</h2>
            <p>Выберите категорию, навыки и формат сделки — мы сохраним фильтры автоматически.</p>
          </div>
          <button type="button" className="button ghost" onClick={handleClearFilters}>
            Сбросить
          </button>
        </div>
        <div className="grid three">
          <div>
            <label htmlFor="category">Категория</label>
            <select id="category" name="category" value={params.get('category') || ''} onChange={handleFilterChange}>
              <option value="">Все категории</option>
              {categories.map((category) => (
                <option key={category.id} value={category.slug}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="skill">Навык</label>
            <select id="skill" name="skill" value={params.get('skill') || ''} onChange={handleFilterChange}>
              <option value="">Все навыки</option>
              {skills.map((skill) => (
                <option key={skill.id} value={skill.slug}>
                  {skill.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="order_type">Тип заказа</label>
            <select id="order_type" name="order_type" value={params.get('order_type') || ''} onChange={handleFilterChange}>
              <option value="">Все</option>
              <option value="urgent">Срочный</option>
              <option value="non_urgent">Не срочный</option>
              <option value="premium">Премиум</option>
              <option value="standard">Обычный</option>
              <option value="company_only">Только компании</option>
              <option value="individual_only">Только фрилансеры</option>
            </select>
          </div>
        </div>
      </section>

      <section className="card saved-filters">
        <div className="saved-filters-header">
          <div>
            <h3>Сохранённые фильтры</h3>
            <p>Назовите комбинацию и возвращайтесь к ней в один клик.</p>
          </div>
          <form className="save-filter-form" onSubmit={handleSaveCurrentFilters}>
            <label htmlFor="filter-name" className="sr-only">
              Название фильтра
            </label>
            <input
              id="filter-name"
              name="filter-name"
              type="text"
              placeholder="Например, UX срочно"
              value={saveLabel}
              onChange={(event) => setSaveLabel(event.target.value)}
            />
            <button type="submit" className="button primary">
              Сохранить
            </button>
          </form>
        </div>
        <div className="filter-chip-list">
          {savedFilters.length === 0 && <span className="muted">Фильтры ещё не сохранены.</span>}
          {savedFilters.map((filter) => (
            <div key={filter.label} className="chip saved">
              <button type="button" onClick={() => handleApplySavedFilter(filter)}>
                {filter.label}
              </button>
              <button
                type="button"
                className="chip-remove"
                aria-label={`Удалить фильтр ${filter.label}`}
                onClick={() => handleDeleteSavedFilter(filter.label)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="card subscribe-card">
        <div>
          <h3>Подписка на новые запросы</h3>
          <p>Получайте подборку по email или в Telegram, как только появляются новые проекты по вашим фильтрам.</p>
        </div>
        <form className="subscribe-form" onSubmit={handleSubscribe}>
          <div className="subscribe-fields">
            <label htmlFor="subscription-email">Email</label>
            <input
              id="subscription-email"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={subscription.email}
              onChange={handleSubscriptionChange}
              required={subscription.channel === 'email'}
            />
          </div>
          <div className="subscribe-fields">
            <label htmlFor="subscription-telegram">Telegram</label>
            <input
              id="subscription-telegram"
              name="telegram"
              type="text"
              placeholder="@username"
              value={subscription.telegram}
              onChange={handleSubscriptionChange}
              required={subscription.channel === 'telegram'}
            />
          </div>
          <fieldset className="channel-selector">
            <legend>Канал доставки</legend>
            <label>
              <input
                type="radio"
                name="channel"
                value="email"
                checked={subscription.channel === 'email'}
                onChange={handleChannelChange}
              />
              Email
            </label>
            <label>
              <input
                type="radio"
                name="channel"
                value="telegram"
                checked={subscription.channel === 'telegram'}
                onChange={handleChannelChange}
              />
              Telegram
            </label>
          </fieldset>
          <button type="submit" className="button primary" disabled={subscriptionStatus === 'pending'}>
            {subscriptionStatus === 'success' ? 'Подписка активна' : 'Подписаться'}
          </button>
        </form>
      </section>

      {loading ? (
        <div className="card">Загрузка заказов...</div>
      ) : orders.length === 0 ? (
        <div className="card empty-state">Не найдено подходящих заказов. Попробуйте изменить фильтры.</div>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => {
            const summary = order.description ? `${order.description.slice(0, 200)}...` : '';
            const skillsList = order.required_skill_details || [];
            return (
              <article key={order.id} className="order-card">
                <header>
                  <div className="order-card-title">
                    <Icon name="task" size={24} decorative />
                    <h2>{order.title}</h2>
                  </div>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{summary}</p>
                <div className="order-meta">
                  <span>Дедлайн: {formatDate(order.deadline, { locale })}</span>
                  <span>
                    Выплата: {order.payment_type === 'hourly' ? 'Почасовая' : 'Фиксированная'} —{' '}
                    {formatCurrency(order.budget, { currency: order.currency, locale })}
                  </span>
                </div>
                <div className="order-tags">
                  {skillsList.map((skill) => (
                    <span key={skill.id} className="tag">
                      {skill.name}
                    </span>
                  ))}
                </div>
                <div className="order-actions">
                  <Link to={buildPath(`/orders/${order.id}`)} className="button ghost">
                    Открыть
                  </Link>
                </div>
                <div className="quick-apply">
                  <label htmlFor={`apply-${order.id}`}>Быстрый отклик</label>
                  <textarea
                    id={`apply-${order.id}`}
                    rows={2}
                    placeholder="Расскажите, почему ваша команда подходит"
                    value={quickApplyMessages[order.id] ?? ''}
                    onChange={(event) => handleQuickApplyChange(order.id, event.target.value)}
                  />
                  <button
                    type="button"
                    className="button primary"
                    onClick={() => handleQuickApplySubmit(order.id)}
                    disabled={quickApplyStatus[order.id] === 'pending'}
                  >
                    {quickApplyStatus[order.id] === 'sent' ? 'Отправлено' : 'Отправить отклик'}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}

      <section className="card faq-card">
        <div className="section-header">
          <div>
            <h2>FAQ по заказам</h2>
            <p>Быстрые ответы для заказчиков и команд.</p>
          </div>
        </div>
        <div className="faq-list">
          {ordersFaq.map((faq) => (
            <article key={faq.question} className="faq-item">
              <h3>{faq.question}</h3>
              <p>{faq.answer}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
