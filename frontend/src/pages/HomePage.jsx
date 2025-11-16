import { Link } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';
import { fetchCategories, fetchOrders } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { formatCurrency, formatDate } from '../utils/formatting.js';
import SeoHelmet from '../components/SeoHelmet.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import { publicContent } from '../mocks/publicContent.js';
import { trackError, trackEvent, useScrollTelemetry } from '../utils/analytics.js';

const stats = [
  {
    value: '1 200+',
    label: 'проектов запущено',
    icon: 'https://img.icons8.com/ios-filled/32/f5f5f5/rocket.png',
  },
  {
    value: '48 ч',
    label: 'среднее время подбора команды',
    icon: 'https://img.icons8.com/ios-filled/32/f5f5f5/alarm-clock.png',
  },
  {
    value: '97%',
    label: 'успешных завершений',
    icon: 'https://img.icons8.com/ios-filled/32/f5f5f5/approval.png',
  },
];

const categoryVisuals = {
  marketing: 'https://img.icons8.com/color/64/marketing.png',
  design: 'https://img.icons8.com/color/64/design--v1.png',
  'искусственный интеллект': 'https://img.icons8.com/color/64/artificial-intelligence.png',
  'artificial-intelligence': 'https://img.icons8.com/color/64/artificial-intelligence.png',
  programming: 'https://img.icons8.com/color/64/source-code.png',
  'программирование': 'https://img.icons8.com/color/64/source-code.png',
  'услуги администрирования': 'https://img.icons8.com/color/64/services.png',
  'uslugi-administrirovaniya': 'https://img.icons8.com/color/64/services.png',
  'услуги видео и аудио': 'https://img.icons8.com/color/64/video-clip.png',
  'uslugi-video-i-audio': 'https://img.icons8.com/color/64/video-clip.png',
  'услуги редактирования': 'https://img.icons8.com/color/64/edit-file.png',
  'uslugi-redaktirovaniya': 'https://img.icons8.com/color/64/edit-file.png',
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

  return 'https://img.icons8.com/color/64/conference-call.png';
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
      <SeoHelmet title={seo.title} description={seo.description} path="/" ogImage={seo.ogImage} jsonLd={{ '@context': 'https://schema.org', '@type': 'Organization', name: publicContent[locale].organization.name, aggregateRating: publicContent[locale].organization.aggregateRating }} />
      <section className="hero home-hero" data-analytics-id="home-hero">
        <div className="home-hero-content">
          <span className="hero-pill">
            <img
              src="https://img.icons8.com/ios-filled/20/f5f5f5/dizzy-person.png"
              alt=""
              aria-hidden="true"
              loading="lazy"
              decoding="async"
            />
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
              <img src={item.icon} alt="" aria-hidden="true" loading="lazy" decoding="async" />
              <div>
                <span>{item.value}</span>
                <p>{item.label}</p>
              </div>
            </div>
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
              <div className="category-card-visual">
                <img src={getCategoryVisual(category)} alt="" aria-hidden="true" loading="lazy" decoding="async" />
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
                    <img
                      src="https://img.icons8.com/ios-filled/28/1f1f1f/lightning-bolt.png"
                      alt=""
                      aria-hidden="true"
                    />
                    <h3>{order.title}</h3>
                  </div>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{description}</p>
                <div className="order-meta">
                  <span>Дедлайн: {formatDate(order.deadline)}</span>
                  <span>
                    Бюджет: {order.payment_type === 'hourly' ? 'Почасовая оплата' : 'Фиксированная'} —{' '}
                    {formatCurrency(order.budget, order.currency)}
                  </span>
                </div>
                <div className="order-tags">
                  {order.required_skill_details?.slice(0, 4).map((skill) => (
                    <span key={skill.id} className="tag">
                      {skill.name}
                    </span>
                  ))}
                </div>
                <Link to={`/orders/${order.id}`} className="button primary">
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
