import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { createOrder, fetchSkills } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import SkillSelector from '../components/SkillSelector.jsx';

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

const deadlineUnits = [
  { value: 'days', label: 'дней' },
  { value: 'weeks', label: 'недель' },
  { value: 'months', label: 'месяцев' },
];

export default function CreateOrderPage() {
  const { user } = useAuth();
  const {
    register,
    handleSubmit,
    formState,
    reset,
    control,
  } = useForm({
    defaultValues: {
      title: '',
      description: '',
      payment_type: paymentTypes[0].value,
      budget: '',
      order_type: orderTypes[0].value,
      deadline_value: 14,
      deadline_unit: 'days',
      required_skills: [],
    },
  });
  const [skills, setSkills] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function loadSkills() {
      try {
        const data = await fetchSkills();
        setSkills(data.results || data);
      } catch (err) {
        console.error('Не удалось загрузить навыки', err);
      }
    }
    loadSkills();
  }, []);

  const deadlineHelper = useMemo(() => {
    return 'Укажите срок выполнения проекта в днях, неделях или месяцах — мы автоматически рассчитаем дату дедлайна.';
  }, []);

  async function onSubmit(formData) {
    try {
      setError('');
      setMessage('');
      const { deadline_value, deadline_unit, required_skills, ...rest } = formData;
      const duration = Number(deadline_value);
      const now = new Date();
      const deadline = new Date(now);

      if (deadline_unit === 'weeks') {
        deadline.setDate(deadline.getDate() + duration * 7);
      } else if (deadline_unit === 'months') {
        deadline.setMonth(deadline.getMonth() + duration);
      } else {
        deadline.setDate(deadline.getDate() + duration);
      }

      const payload = {
        ...rest,
        deadline: deadline.toISOString(),
        budget: Number(rest.budget),
        required_skills: (required_skills || []).map((item) => Number(item)),
      };

      const created = await createOrder(payload);
      setMessage('Заказ успешно опубликован!');
      reset({
        title: '',
        description: '',
        payment_type: paymentTypes[0].value,
        budget: '',
        order_type: orderTypes[0].value,
        deadline_value: 14,
        deadline_unit: 'days',
        required_skills: [],
      });
      setTimeout(() => navigate(`/orders/${created.id}`), 1500);
    } catch (err) {
      setError('Не удалось создать заказ. Проверьте введённые данные.');
    }
  }

  if (!user?.profile?.is_verified) {
    return (
      <div className="card" style={{ maxWidth: '640px', margin: '0 auto' }}>
        <h1>Публикация заказов доступна только верифицированным клиентам</h1>
        <p style={{ marginBottom: '1rem' }}>
          Пройдите процедуру проверки документов, чтобы размещать новые проекты и управлять ими.
        </p>
        <Link className="button primary" to="/verification">
          Перейти к верификации
        </Link>
      </div>
    );
  }

  return (
    <div className="card create-order-card">
      <header className="form-header">
        <div>
          <span className="form-pill">
            <img src="https://img.icons8.com/ios-filled/24/1f1f1f/flash-on.png" alt="" aria-hidden="true" />
            Новый заказ
          </span>
          <h1>Опубликовать заказ</h1>
          <p>Расскажите о задаче, определите бюджет и отметьте ключевые навыки, которые понадобятся исполнителям.</p>
        </div>
      </header>

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}

      <form onSubmit={handleSubmit(onSubmit)} className="form-grid">
        <div className="form-section full">
          <label htmlFor="title">Название проекта</label>
          <input id="title" placeholder="Например, разработка корпоративного сайта" {...register('title', { required: true })} />
        </div>
        <div className="form-section full">
          <label htmlFor="description">Описание</label>
          <textarea
            id="description"
            rows="6"
            placeholder="Опишите цель проекта, ожидаемый результат и текущий статус"
            {...register('description', { required: true })}
          />
        </div>
        <div className="form-section">
          <label htmlFor="deadline_value">Срок выполнения</label>
          <div className="deadline-input">
            <input
              id="deadline_value"
              type="number"
              min="1"
              {...register('deadline_value', { required: true, valueAsNumber: true, min: 1 })}
            />
            <select id="deadline_unit" {...register('deadline_unit', { required: true })}>
              {deadlineUnits.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <small>{deadlineHelper}</small>
        </div>
        <div className="form-section">
          <label htmlFor="payment_type">Тип оплаты</label>
          <select id="payment_type" {...register('payment_type', { required: true })}>
            {paymentTypes.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-section">
          <label htmlFor="budget">Сумма выплаты</label>
          <input
            id="budget"
            type="number"
            min="0"
            step="0.01"
            placeholder="Укажите бюджет в сумах"
            {...register('budget', { required: true })}
          />
        </div>
        <div className="form-section">
          <label htmlFor="order_type">Роль заказа</label>
          <select id="order_type" {...register('order_type', { required: true })}>
            {orderTypes.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-section full">
          <SkillSelector control={control} name="required_skills" skills={skills} />
        </div>
        <div className="form-actions">
          <button className="button primary" type="submit" disabled={formState.isSubmitting}>
            Опубликовать заказ
          </button>
        </div>
      </form>
    </div>
  );
}
