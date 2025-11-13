import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { fetchCategories, fetchOrders, fetchSkills } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { formatCurrency } from '../utils/formatCurrency.js';

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
  const { isAuthenticated, user } = useAuth();

  const role = user?.profile?.role || user?.role;

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
    <div className="orders-page">
      <section className="card soft page-header">
        <div className="page-header-content">
          <span className="page-header-icon">
            <img src="https://img.icons8.com/ios-filled/32/1f1f1f/task.png" alt="Иконка заказов" />
          </span>
          <div>
            <h1>Все заказы</h1>
            <p>Фильтруйте открытые проекты по категориям, навыкам и формату сотрудничества.</p>
          </div>
        </div>
        {role === 'client' && isAuthenticated && (
          <Link to="/orders/create" className="button primary">
            Создать заказ
          </Link>
        )}
      </section>

      <section className="card filter-card">
        <h2>Подбор параметров</h2>
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
              <option value="company_only">Только компании фрилансеров</option>
              <option value="individual_only">Только одиночный фрилансер</option>
            </select>
          </div>
        </div>
      </section>

      {loading ? (
        <div className="card">Загрузка заказов...</div>
      ) : orders.length === 0 ? (
        <div className="card empty-state">Не найдено подходящих заказов. Попробуйте изменить фильтры.</div>
      ) : (
        <div className="orders-grid">
          {orders.map((order) => {
            const summary = order.description ? `${order.description.slice(0, 200)}...` : '';
            return (
              <article key={order.id} className="order-card">
                <header>
                  <div className="order-card-title">
                    <img
                      src="https://img.icons8.com/ios-filled/28/1f1f1f/todo-list.png"
                      alt=""
                      aria-hidden="true"
                    />
                    <h2>{order.title}</h2>
                  </div>
                  <span className="status">{orderTypeLabels[order.order_type] || order.order_type}</span>
                </header>
                <p>{summary}</p>
                <div className="order-meta">
                  <span>Дедлайн: {new Date(order.deadline).toLocaleDateString()}</span>
                  <span>
                    Выплата: {order.payment_type === 'hourly' ? 'Почасовая' : 'Фиксированная'} —{' '}
                    {formatCurrency(order.budget, order.currency)}
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
