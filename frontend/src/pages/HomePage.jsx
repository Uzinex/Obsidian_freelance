import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { fetchCategories, fetchOrders } from '../api/client.js';

const stats = [
  { value: '1 200+', label: 'проектов запущено' },
  { value: '48 ч', label: 'среднее время подбора команды' },
  { value: '97%', label: 'успешных завершений' },
];

const steps = [
  {
    title: 'Опишите задачу',
    description: 'Укажите бюджет, сроки и необходимые навыки — мы поможем собрать идеальный бриф.',
  },
  {
    title: 'Подберите специалистов',
    description: 'Используйте фильтры по категориям и навыкам или доверьте подбор нашим ассистентам.',
  },
  {
    title: 'Запустите проект',
    description: 'Отслеживайте прогресс, общайтесь в чате и получайте отчеты прямо в личном кабинете.',
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
      }
    }
    loadData();
  }, []);

  return (
    <div className="homepage">
      <section className="hero home-hero">
        <div>
          <h1>Объединяем лучшие команды для сложных проектов</h1>
          <p>
            Платформа Obsidian Freelance помогает заказчикам запускать цифровые продукты, а специалистам — находить
            задачи уровня мечты. Все процессы прозрачны, а сделки защищены.
          </p>
          <div className="hero-actions">
            <Link className="button primary" to="/register">
              Начать сейчас
            </Link>
            <Link className="button secondary" to="/orders">
              Смотреть работы
            </Link>
          </div>
        </div>
        <div className="hero-stats">
          {stats.map((item) => (
            <div key={item.label} className="hero-stat">
              <span>{item.value}</span>
              <p>{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card category-section">
        <header className="section-header">
          <div>
            <h2>Категории работ</h2>
            <p>Выберите направление и найдите проекты или специалистов в несколько кликов.</p>
          </div>
          <Link to="/orders" className="button secondary">
            Все работы
          </Link>
        </header>
        <div className="category-grid">
          {categories.map((category) => (
            <article key={category.id} className="category-card">
              <div className="category-card-body">
                <h3>{category.name}</h3>
                <p>{category.description}</p>
              </div>
              <Link to={`/orders?category=${category.slug}`} className="button ghost">
                Смотреть проекты
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="card steps-section">
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

      <section className="card latest-orders">
        <header className="section-header">
          <div>
            <h2>Свежие работы</h2>
            <p>Актуальные запросы от проверенных заказчиков.</p>
          </div>
          <Link to="/orders" className="button secondary">
            Смотреть все
          </Link>
        </header>
        <div className="grid two">
          {latestOrders.map((order) => {
            const description = order.description ? `${order.description.slice(0, 180)}...` : '';
            return (
              <article key={order.id} className="order-card">
                <header>
                  <h3>{order.title}</h3>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{description}</p>
                <div className="order-meta">
                  <span>Дедлайн: {new Date(order.deadline).toLocaleDateString()}</span>
                  <span>
                    Бюджет: {order.payment_type === 'hourly' ? 'Почасовая оплата' : 'Фиксированная'} — {order.budget} сум
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
