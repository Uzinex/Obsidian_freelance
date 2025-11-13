import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { createOrder, fetchSkills } from '../api/client.js';

const paymentTypes = [
  { value: 'hourly', label: 'Почасовая оплата' },
  { value: 'fixed', label: 'Фиксированная оплата' },
];

const orderTypes = [
  { value: 'urgent', label: 'Срочный заказ' },
  { value: 'non_urgent', label: 'Не срочный заказ' },
  { value: 'premium', label: 'Премиум заказ' },
  { value: 'standard', label: 'Обычный заказ' },
  { value: 'company_only', label: 'Только компании фрилансеров' },
  { value: 'individual_only', label: 'Только одному фрилансеру' },
];

export default function CreateOrderPage() {
  const { register, handleSubmit, formState, reset } = useForm();
  const [skills, setSkills] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function loadSkills() {
      try {
        const data = await fetchSkills();
        setSkills(data);
      } catch (err) {
        console.error('Не удалось загрузить навыки', err);
      }
    }
    loadSkills();
  }, []);

  async function onSubmit(data) {
    try {
      setError('');
      setMessage('');
      const payload = {
        ...data,
        budget: Number(data.budget),
        required_skills: (data.required_skills || []).map((item) => Number(item)),
      };
      const created = await createOrder(payload);
      setMessage('Заказ успешно опубликован!');
      reset();
      setTimeout(() => navigate(`/orders/${created.id}`), 1500);
    } catch (err) {
      setError('Не удалось создать заказ. Проверьте введённые данные.');
    }
  }

  return (
    <div className="card" style={{ maxWidth: '720px', margin: '0 auto' }}>
      <h1>Опубликовать заказ</h1>
      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}
      <form onSubmit={handleSubmit(onSubmit)} className="grid two">
        <div style={{ gridColumn: '1 / -1' }}>
          <label htmlFor="title">Название проекта</label>
          <input id="title" {...register('title', { required: true })} />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label htmlFor="description">Описание</label>
          <textarea id="description" rows="6" {...register('description', { required: true })} />
        </div>
        <div>
          <label htmlFor="deadline">Дедлайн</label>
          <input id="deadline" type="datetime-local" {...register('deadline', { required: true })} />
        </div>
        <div>
          <label htmlFor="payment_type">Тип оплаты</label>
          <select id="payment_type" {...register('payment_type', { required: true })}>
            {paymentTypes.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="budget">Сумма выплаты</label>
          <input id="budget" type="number" step="0.01" {...register('budget', { required: true })} />
        </div>
        <div>
          <label htmlFor="order_type">Роль заказа</label>
          <select id="order_type" {...register('order_type', { required: true })}>
            {orderTypes.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label htmlFor="required_skills">Требуемые навыки</label>
          <select id="required_skills" multiple size={Math.min(12, skills.length)} {...register('required_skills', { required: true })}>
            {skills.map((skill) => (
              <option key={skill.id} value={skill.id}>
                {skill.name}
              </option>
            ))}
          </select>
          <small>Зажмите Ctrl / Cmd для выбора нескольких навыков.</small>
        </div>
        <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
          <button className="button primary" type="submit" disabled={formState.isSubmitting}>
            Опубликовать заказ
          </button>
        </div>
      </form>
    </div>
  );
}
