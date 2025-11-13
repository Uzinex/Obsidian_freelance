import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { fetchCategories, fetchOrders, fetchSkills } from '../api/client.js';

const orderTypeLabels = {
  urgent: 'Срочный',
  non_urgent: 'Несрочный',
  premium: 'Премиум',
  standard: 'Стандартный',
  company_only: 'Только компании',
  individual_only: 'Только фрилансеры',
};

export default function OrdersPage() {
  const [params, setParams] = useSearchParams();
  const [orders, setOrders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

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
    loadFilters();
  }, []);

  useEffect(() => {
    async function loadOrders() {
      setLoading(true);
      try {
        const query = Object.fromEntries(params.entries());
        const data = await fetchOrders(query);
        setOrders(data.results || data);
      } catch (error) {
        console.error('Не удалось загрузить заказы', error);
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, [params]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const next = new URLSearchParams(params);
    if (value) {
      next.set(name, value);
    } else {
      next.delete(name);
    }
    setParams(next);
  };

  return (
    <div className="grid" style={{ gap: '2rem' }}>
      <section className="card">
        <h1>Все заказы</h1>
        <div className="grid two">
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
              <option value="company_only">Только компании фрилансеров</option>
              <option value="individual_only">Только одиночный фрилансер</option>
            </select>
          </div>
        </div>
      </section>

      {loading ? (
        <div className="card">Загрузка заказов...</div>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => {
            const summary = order.description ? `${order.description.slice(0, 200)}...` : '';
            return (
              <article key={order.id} className="order-card">
                <header>
                  <h2>{order.title}</h2>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{summary}</p>
                <div className="order-meta">
                  <span>Дедлайн: {new Date(order.deadline).toLocaleString()}</span>
                  <span>
                    Выплата: {order.payment_type === 'hourly' ? 'Почасовая' : 'Фиксированная'} — {order.budget} сум
                  </span>
                </div>
                <div className="order-tags">
                  {order.required_skill_details?.map((skill) => (
                    <span key={skill.id} className="tag">
                      {skill.name}
                    </span>
                  ))}
                </div>
                <Link to={`/orders/${order.id}`} className="button primary">
                  Открыть
                </Link>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
