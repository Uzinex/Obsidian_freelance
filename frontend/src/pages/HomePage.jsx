import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { fetchCategories, fetchOrders } from '../api/client.js';

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
        setCategories(categoryData);
        setLatestOrders(orderData.results || orderData);
      } catch (error) {
        console.error('Не удалось загрузить данные', error);
      }
    }
    loadData();
  }, []);

  return (
    <div className="grid" style={{ gap: '3rem' }}>
      <section className="hero">
        <h1>Obsidian Freelance</h1>
        <p>
          Первая в регионе платформа, объединяющая профессиональных фрилансеров и надежных заказчиков.
          Присоединяйтесь, чтобы создавать, сотрудничать и расти.
        </p>
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link className="button primary" to="/register">
            Начать сейчас
          </Link>
          <Link className="button secondary" to="/orders">
            Смотреть заказы
          </Link>
        </div>
      </section>

      <section>
        <h2 className="section-title">Категории проектов</h2>
        <div className="grid three">
          {categories.map((category) => (
            <article key={category.id} className="card">
              <h3>{category.name}</h3>
              <p>{category.description}</p>
              <Link to={`/orders?category=${category.slug}`} className="button secondary">
                Смотреть заказы
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="section-title">Новые заказы</h2>
        <div className="grid two">
          {latestOrders.map((order) => {
            const description = order.description ? `${order.description.slice(0, 140)}...` : '';
            return (
              <article key={order.id} className="card">
                <header style={{ marginBottom: '1rem' }}>
                  <h3>{order.title}</h3>
                </header>
                <p style={{ minHeight: '4rem' }}>{description}</p>
              <div className="status">Дедлайн: {new Date(order.deadline).toLocaleDateString()}</div>
              <div style={{ margin: '1rem 0' }}>
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
