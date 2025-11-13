import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { applyToOrder, fetchOrder } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function OrderDetailPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    async function loadOrder() {
      try {
        const data = await fetchOrder(orderId);
        setOrder(data);
      } catch (err) {
        setError('Не удалось загрузить заказ.');
      }
    }
    loadOrder();
  }, [orderId]);

  const isFreelancer = user?.profile?.role === 'freelancer';
  const isVerified = Boolean(user?.profile?.is_verified);

  async function handleApply() {
    if (!isFreelancer) {
      setError('Только фрилансеры могут откликаться на заказы.');
      return;
    }
    if (!isVerified) {
      setError('Для отклика необходимо пройти верификацию.');
      return;
    }
    try {
      setError('');
      setMessage('');
      await applyToOrder({ order: order.id, cover_letter: 'Готов взяться за проект.' });
      setMessage('Ваш отклик отправлен заказчику.');
    } catch (err) {
      setError('Не удалось отправить отклик. Возможно, вы уже откликались.');
    }
  }

  if (!order) {
    return <div className="card">Загрузка заказа...</div>;
  }

  return (
    <div className="card" style={{ maxWidth: '860px', margin: '0 auto' }}>
      <h1>{order.title}</h1>
      <div className="status">Статус: {order.status}</div>
      <p>{order.description}</p>
      <div style={{ margin: '1rem 0' }}>
        <strong>Оплата:</strong> {order.payment_type === 'hourly' ? 'Почасовая' : 'Фиксированная'} — {order.budget} сум
      </div>
      <div className="status">Дедлайн: {new Date(order.deadline).toLocaleString()}</div>
      <div style={{ margin: '1rem 0' }}>
        <strong>Навыки:</strong>
        <div>
          {order.required_skill_details?.map((skill) => (
            <span key={skill.id} className="tag">
              {skill.name}
            </span>
          ))}
        </div>
      </div>
      <div>
        <strong>Заказчик:</strong>{' '}
        {order.client?.user
          ? `${order.client.user.last_name} ${order.client.user.first_name}`.trim()
          : 'Неизвестно'}
      </div>
      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}
      {isFreelancer && (
        <button
          className="button primary"
          type="button"
          onClick={handleApply}
          disabled={!isVerified}
        >
          {isVerified ? 'Откликнуться' : 'Требуется верификация'}
        </button>
      )}
    </div>
  );
}
