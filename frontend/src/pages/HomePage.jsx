import { Link } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';
import { fetchCategories, fetchOrders } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { formatCurrency, formatDate } from '../utils/formatting.js';
import SeoHelmet from '../components/SeoHelmet.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import { publicContent } from '../mocks/publicContent.js';
import { trackError, trackEvent, useScrollTelemetry } from '../utils/analytics.js';
import Icon from '../components/Icon.jsx';

const stats = [
  {
    value: '1 200+',
    label: 'проектов запущено',
    icon: 'rocket',
  },
  {
    value: '48 ч',
    label: 'среднее время подбора команды',
    icon: 'timer',
  },
  {
    value: '97%',
    label: 'успешных завершений',
    icon: 'shield',
  },
];

const categoryVisuals = {
  marketing: 'chart',
  design: 'idea',
  'искусственный интеллект': 'spark',
  'artificial-intelligence': 'spark',
  programming: 'orders',
  'программирование': 'orders',
  'услуги администрирования': 'shield',
  'uslugi-administrirovaniya': 'shield',
  'услуги видео и аудио': 'lightning',
  'uslugi-video-i-audio': 'lightning',
  'услуги редактирования': 'todo',
  'uslugi-redaktirovaniya': 'todo',
};

const getCategoryVisual = (category) => {
  const normalizedName = category.name?.toLowerCase().trim();
  const normalizedSlug = category.slug?.toLowerCase().trim();

  const keysToCheck = [
    normalizedSlug,
    normalizedSlug?.replace(/-/g, ' '),
    normalizedSlug?.replace(/-/g, '_'),
    normalizedName,
    normalizedName?.replace(/\s+/g, '-'),
  ].filter(Boolean);

  for (const key of keysToCheck) {
    if (categoryVisuals[key]) {
      return categoryVisuals[key];
    }
  }

  return 'bookmark';
};

const steps = [
  {
    title: 'Опишите задачу',
    description:
      'Укажите бюджет, сроки и необходимые навыки — мы поможем собрать идеальный бриф.',
  },
  {
    title: 'Подберите специалистов',
    description:
      'Используйте фильтры по категориям и навыкам или доверьте подбор нашим ассистентам.',
  },
  {
    title: 'Запустите проект',
    description:
      'Отслеживайте прогресс, общайтесь в чате и получайте отчеты прямо в личном кабинете.',
  },
];

const orderTypeLabels = {
  urgent: 'Срочный',
  non_urgent: 'Несрочный',
  premium: 'Премиум',
  standard: 'Стандартный',
  company_only: 'Только компании',
  individual_only: 'Только фрилансеры',
};

export default function HomePage() {
  const [categories, setCategories] = useState([]);
  const [latestOrders, setLatestOrders] = useState([]);
  const { isAuthenticated } = useAuth();
  const { locale, buildPath } = useLocale();
  const seo = publicContent[locale].seo.home;
  const localizedOrdersPath = buildPath('/orders');
  const localizedFreelancersPath = buildPath('/freelancers');
  const reviews = publicContent[locale].reviews;
  const organization = publicContent[locale].organization;

  const organizationLd = useMemo(
    () => ({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: organization.name,
      url: organization.url,
      logo: organization.logo,
      sameAs: organization.sameAs,
      aggregateRating: organization.aggregateRating,
      review: reviews.map((review) => ({
        '@type': 'Review',
        author: { '@type': 'Person', name: review.author },
        reviewBody: review.review,
        reviewRating: { '@type': 'Rating', ratingValue: review.rating },
      })),
    }),
    [organization, reviews],
  );

  const slaBadges = useMemo(
    () =>
      locale === 'uz'
        ? [
            { label: 'SLA 2 soat', description: 'Moderatorlar 24/7 rejimida javob beradi.' },
            { label: 'Escrow changelog', description: 'Har yangilanish ochiq changelogda.' },
            { label: 'Verifikatsiya', description: 'Har profil uchun KYC va qo‘lda tekshiruv.' },
          ]
        : [
            { label: 'SLA 2 часа', description: 'Ответ поддержки и куратора в течение двух часов.' },
            { label: 'Escrow changelog', description: 'Все изменения логики escrow публичны.' },
            { label: 'Верификация', description: 'Удостоверения и компании проходят ручную проверку.' },
          ],
    [locale],
  );

  useScrollTelemetry(['home-hero', 'home-categories', 'home-steps', 'home-orders'], {
    page: 'landing',
    locale,
  });

  useEffect(() => {
    trackEvent('landing_view', { locale });
  }, [locale]);

  useEffect(() => {
    async function loadData() {
      try {
        const [categoryData, orderData] = await Promise.all([
          fetchCategories(),
          fetchOrders({ ordering: '-created_at', page_size: 6 }),
        ]);
        setCategories(categoryData.results || categoryData);
        setLatestOrders(orderData.results || orderData);
      } catch (error) {
        console.error('Не удалось загрузить данные', error);
        trackError('landing_data_error', error, { locale });
      }
    }
    loadData();
  }, [locale]);

  const primaryAction = useMemo(
    () => ({
      to: isAuthenticated ? localizedOrdersPath : '/register',
      label: isAuthenticated ? 'Перейти к заказам' : 'Начать сейчас',
    }),
    [isAuthenticated, localizedOrdersPath],
  );

  return (
    <div className="homepage" data-analytics-id="home">
      <SeoHelmet title={seo.title} description={seo.description} path="/" ogImage={seo.ogImage} jsonLd={organizationLd} />
      <section className="hero home-hero" data-analytics-id="home-hero">
        <div className="home-hero-content">
          <span className="hero-pill">
            <Icon name="spark" size={18} decorative />
            Платформа для сложных цифровых задач
          </span>
          <h1>Объединяем лучшие команды для амбициозных проектов</h1>
          <p>
            Obsidian Freelance помогает заказчикам запускать цифровые продукты, а специалистам — находить задачи
            уровня мечты. Все процессы прозрачны, а сделки защищены.
          </p>
          <div className="hero-actions">
            <Link
              className="button primary"
              to={primaryAction.to}
              onClick={() =>
                trackEvent('landing_signup_click', {
                  locale,
                  authenticated: isAuthenticated,
                })
              }
            >
              {primaryAction.label}
            </Link>
            <Link
              className="button ghost"
              to={localizedOrdersPath}
              onClick={() =>
                trackEvent('landing_post_job_click', {
                  locale,
                  authenticated: isAuthenticated,
                })
              }
            >
              Смотреть работы
            </Link>
            <Link
              className="button ghost"
              to={localizedFreelancersPath}
              onClick={() => trackEvent('landing_invite_freelancer', { locale })}
            >
              Пригласить фрилансера
            </Link>
          </div>
        </div>
        <div className="hero-stats">
          {stats.map((item) => (
            <div key={item.label} className="hero-stat">
              <Icon name={item.icon} size={28} decorative />
              <div>
                <span>{item.value}</span>
                <p>{item.label}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card trust-card" data-analytics-id="home-trust">
        <div className="trust-badges">
          {slaBadges.map((badge) => (
            <div key={badge.label} className="trust-badge">
              <Icon name="shield" size={20} decorative />
              <div>
                <strong>{badge.label}</strong>
                <p>{badge.description}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="testimonial-grid">
          {reviews.map((review) => (
            <article key={review.author} className="testimonial-card">
              <header>
                <Icon name="badge" size={24} decorative />
                <div>
                  <strong>{review.author}</strong>
                  <span>{review.role}</span>
                </div>
              </header>
              <p>“{review.review}”</p>
              <div className="rating" aria-label={`Оценка ${review.rating} из 5`}>
                {Array.from({ length: review.rating }).map((_, index) => (
                  <Icon key={index} name="check" size={16} decorative />
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="card category-section" data-analytics-id="home-categories">
        <header className="section-header">
          <div>
            <h2>Категории работ</h2>
            <p>Выберите направление и найдите проекты или специалистов в несколько кликов.</p>
          </div>
          <Link to={localizedOrdersPath} className="button ghost">
            Все работы
          </Link>
        </header>
        <div className="category-grid">
          {categories.map((category) => (
            <Link key={category.id} to={buildPath(`/orders?category=${category.slug}`)} className="category-card">
              <div className="category-card-visual" aria-hidden="true">
                <Icon name={getCategoryVisual(category)} size={32} decorative />
              </div>
              <div className="category-card-body">
                <h3>{category.name}</h3>
                <p>{category.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="card steps-section" data-analytics-id="home-steps">
        <h2>Как работает платформа</h2>
        <div className="grid three">
          {steps.map((step, index) => (
            <article key={step.title} className="step-card">
              <div className="step-index">0{index + 1}</div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card latest-orders" data-analytics-id="home-orders">
        <header className="section-header">
          <div>
            <h2>Свежие работы</h2>
            <p>Актуальные запросы от проверенных заказчиков.</p>
          </div>
          <Link to={localizedOrdersPath} className="button ghost">
            Смотреть все
          </Link>
        </header>
        <div className="grid two">
          {latestOrders.map((order) => {
            const description = order.description ? `${order.description.slice(0, 180)}...` : '';
            return (
              <article key={order.id} className="order-card">
                <header>
                  <div className="order-card-title">
                    <Icon name="lightning" size={22} decorative />
                    <h3>{order.title}</h3>
                  </div>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{description}</p>
                <div className="order-meta">
                  <span>Дедлайн: {formatDate(order.deadline, { locale })}</span>
                  <span>
                    Бюджет: {order.payment_type === 'hourly' ? 'Почасовая оплата' : 'Фиксированная'} —{' '}
                    {formatCurrency(order.budget, { currency: order.currency, locale })}
                  </span>
                </div>
                <div className="order-tags">
                  {order.required_skill_details?.slice(0, 4).map((skill) => (
                    <span key={skill.id} className="tag">
                      {skill.name}
                    </span>
                  ))}
                </div>
                <Link to={buildPath(`/orders/${order.id}`)} className="button primary">
                  Подробнее
                </Link>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
