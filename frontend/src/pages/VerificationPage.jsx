import { useForm } from 'react-hook-form';
import { useState } from 'react';
import { submitVerification } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';

const documents = [
  { value: 'driver_license', label: 'Водительские права' },
  { value: 'passport', label: 'Паспорт' },
  { value: 'id_card', label: 'ID карта' },
];

export default function VerificationPage() {
  const { user } = useAuth();
  const form = useForm({ defaultValues: { document_type: 'passport' } });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

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
      {message && <div className="alert success">{message}</div>}
      {error && <div className="alert">{error}</div>}
      <form onSubmit={form.handleSubmit(onSubmit)} encType="multipart/form-data" className="grid">
        <label htmlFor="document_type">Документ</label>
        <select id="document_type" {...form.register('document_type')}>
          {documents.map((doc) => (
            <option key={doc.value} value={doc.value}>
              {doc.label}
            </option>
          ))}
        </select>

        <label htmlFor="document_series">Серия документа</label>
        <input id="document_series" {...form.register('document_series', { required: true })} />

        <label htmlFor="document_number">Номер документа</label>
        <input id="document_number" {...form.register('document_number', { required: true })} />

        <label htmlFor="document_image">Фото документа</label>
        <input id="document_image" type="file" accept="image/*" {...form.register('document_image', { required: true })} />

        <div className="form-actions">
          <button className="button primary" type="submit">
            Отправить на проверку
          </button>
        </div>
      </form>
    </div>
  );
}
