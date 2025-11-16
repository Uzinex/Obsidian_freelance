import { useEffect, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { fetchVerificationRequests, submitVerification } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { formatDateTime } from '../utils/formatting.js';

const documents = [
  { value: 'driver_license', label: 'Водительское удостоверение' },
  { value: 'passport', label: 'Паспорт' },
  { value: 'id_card', label: 'ID карта' },
];

const statusLabels = {
  pending: 'На рассмотрении',
  approved: 'Одобрено',
  rejected: 'Отклонено',
};

export default function VerificationPage() {
  const { user } = useAuth();
  const form = useForm({ defaultValues: { document_type: 'passport' } });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  const latestRequest = useMemo(() => requests[0] || null, [requests]);
  const statusLabel = latestRequest ? statusLabels[latestRequest.status] || latestRequest.status : '';
  const isPending = latestRequest?.status === 'pending';
  const isApproved = latestRequest?.status === 'approved';
  const isRejected = latestRequest?.status === 'rejected';

  useEffect(() => {
    loadRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadRequests() {
    try {
      setLoading(true);
      const data = await fetchVerificationRequests();
      setRequests(data.results || data);
    } catch (err) {
      console.error('Не удалось получить список верификаций', err);
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(data) {
    try {
      setMessage('');
      setError('');
      const formData = new FormData();
      formData.append('profile', user?.profile?.id);
      formData.append('document_type', data.document_type);
      formData.append('document_series', data.document_series);
      formData.append('document_number', data.document_number);
      formData.append('document_image', data.document_image[0]);
      await submitVerification(formData);
      setMessage('Заявка на верификацию отправлена. Ожидайте подтверждения администратора.');
      await loadRequests();
      form.reset({ document_type: data.document_type });
    } catch (err) {
      setError('Не удалось отправить запрос на верификацию.');
    }
  }

  if (!user?.profile) {
    return <div className="card">Сначала заполните профиль.</div>;
  }

  return (
    <div className="card" style={{ maxWidth: '560px', margin: '0 auto' }}>
      <h1>Верификация аккаунта</h1>
      <p>ФИО: {user.full_name || `${user.last_name} ${user.first_name}`}</p>

      {loading ? (
        <div className="alert">Загрузка статуса верификации...</div>
      ) : (
        <>
          {latestRequest && (
            <div className="status" style={{ marginBottom: '1rem' }}>
              <strong>Текущий статус:</strong> {statusLabel}
            </div>
          )}
          {latestRequest?.reviewer_note && (
            <div className="alert" style={{ marginBottom: '1rem' }}>
              Комментарий администратора: {latestRequest.reviewer_note}
            </div>
          )}
          {isApproved && (
            <div className="alert success" style={{ marginBottom: '1rem' }}>
              Ваша заявка одобрена. Теперь вы можете полноценно пользоваться платформой.
            </div>
          )}
          {isPending && (
            <div className="alert" style={{ marginBottom: '1rem' }}>
              Заявка находится на рассмотрении. Вы получите уведомление после проверки.
            </div>
          )}
          {isRejected && (
            <div className="alert" style={{ marginBottom: '1rem' }}>
              Верификация отклонена. Проверьте комментарий администратора и отправьте заявку повторно.
            </div>
          )}
        </>
      )}

      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}

      <form
        onSubmit={form.handleSubmit(onSubmit)}
        encType="multipart/form-data"
        className="grid"
        style={{ opacity: isPending || isApproved ? 0.6 : 1 }}
      >
        <label htmlFor="document_type">Документ</label>
        <select id="document_type" {...form.register('document_type')} disabled={isPending || isApproved}>
          {documents.map((doc) => (
            <option key={doc.value} value={doc.value}>
              {doc.label}
            </option>
          ))}
        </select>

        <label htmlFor="document_series">Серия документа</label>
        <input
          id="document_series"
          {...form.register('document_series', { required: true })}
          disabled={isPending || isApproved}
        />

        <label htmlFor="document_number">Номер документа</label>
        <input
          id="document_number"
          {...form.register('document_number', { required: true })}
          disabled={isPending || isApproved}
        />

        <label htmlFor="document_image">Фото документа</label>
        <input
          id="document_image"
          type="file"
          accept="image/*"
          {...form.register('document_image', { required: true })}
          disabled={isPending || isApproved}
        />

        <div className="form-actions">
          <button className="button primary" type="submit" disabled={isPending || isApproved}>
            {isApproved ? 'Заявка одобрена' : 'Отправить на проверку'}
          </button>
        </div>
      </form>

      {requests.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2 style={{ fontSize: '1.1rem' }}>История заявок</h2>
          <ul style={{ paddingLeft: '1.25rem', marginTop: '0.5rem' }}>
            {requests.map((item) => (
              <li key={item.id}>
                {formatDateTime(item.created_at)} — {statusLabels[item.status] || item.status}
                {item.reviewer_note ? ` (Комментарий: ${item.reviewer_note})` : ''}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
