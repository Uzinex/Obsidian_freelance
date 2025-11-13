import { useEffect, useMemo, useState } from 'react';
import {
  fetchVerificationRequests,
  reviewVerificationRequest,
} from '../api/client.js';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const documentLabels = {
  passport: 'Паспорт',
  driver_license: 'Водительское удостоверение',
  id_card: 'ID карта',
};

const statusLabels = {
  pending: 'На рассмотрении',
  approved: 'Одобрено',
  rejected: 'Отклонено',
};

function resolveMediaPath(path) {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `${API_BASE_URL}${path}`;
}

export default function VerificationRequestsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notes, setNotes] = useState({});
  const [success, setSuccess] = useState('');

  const pendingCount = useMemo(
    () => requests.filter((item) => item.status === 'pending').length,
    [requests],
  );

  useEffect(() => {
    loadRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadRequests() {
    try {
      setLoading(true);
      setError('');
      const data = await fetchVerificationRequests();
      setRequests(data.results || data);
      setNotes({});
    } catch (err) {
      setError('Не удалось получить заявки на верификацию.');
    } finally {
      setLoading(false);
    }
  }

  function handleNoteChange(id, value) {
    setNotes((prev) => ({ ...prev, [id]: value }));
  }

  async function handleDecision(id, action) {
    try {
      setError('');
      setSuccess('');
      await reviewVerificationRequest(id, action, { note: notes[id] || '' });
      setSuccess(
        action === 'approve'
          ? 'Заявка успешно одобрена.'
          : 'Заявка отклонена. Пользователь уведомлен.',
      );
      await loadRequests();
    } catch (err) {
      setError('Не удалось обновить статус заявки.');
    }
  }

  if (loading) {
    return <div className="card">Загрузка заявок...</div>;
  }

  return (
    <div className="card" style={{ maxWidth: '1024px', margin: '0 auto' }}>
      <header className="form-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <span className="form-pill">
            <img
              src="https://img.icons8.com/ios-filled/24/1f1f1f/checked-user-male.png"
              alt=""
              aria-hidden="true"
            />
            Администрирование
          </span>
          <h1>Заявки на верификацию</h1>
          <p>
            Проверьте документы пользователей и подтвердите или отклоните заявки с
            комментарием. {pendingCount ? `Сейчас ожидает ${pendingCount} заявок.` : 'Нет заявок в ожидании.'}
          </p>
        </div>
      </header>

      {success && <div className="alert success">{success}</div>}
      {error && <div className="alert">{error}</div>}

      {requests.length === 0 ? (
        <p>Пока нет ни одной заявки на верификацию.</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th>Документ</th>
                <th>Статус</th>
                <th>Комментарий</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => {
                const documentLabel = documentLabels[request.document_type] || request.document_type;
                const statusLabel = statusLabels[request.status] || request.status;
                const profileUser = request.profile_details?.user || {};
                const profileName = `${profileUser.last_name || ''} ${profileUser.first_name || ''}`.trim() ||
                  profileUser.nickname ||
                  'Без имени';
                const mediaUrl = resolveMediaPath(request.document_image);
                return (
                  <tr key={request.id}>
                    <td>
                      <div className="stack">
                        <strong>{profileName}</strong>
                        <small>Профиль #{request.profile}</small>
                        <small>Создано: {new Date(request.created_at).toLocaleString()}</small>
                        {request.reviewed_at && (
                          <small>Обновлено: {new Date(request.reviewed_at).toLocaleString()}</small>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="stack">
                        <span>{documentLabel}</span>
                        <small>
                          Серия: {request.document_series}
                          <br />
                          Номер: {request.document_number}
                        </small>
                        {mediaUrl && (
                          <a href={mediaUrl} target="_blank" rel="noreferrer" className="link">
                            Открыть документ
                          </a>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className={`status-badge status-${request.status}`}>
                        {statusLabel}
                      </div>
                      {request.reviewer_note && (
                        <small>Комментарий: {request.reviewer_note}</small>
                      )}
                    </td>
                    <td>
                      <textarea
                        rows={3}
                        placeholder="Комментарий администратора"
                        value={notes[request.id] ?? ''}
                        onChange={(event) => handleNoteChange(request.id, event.target.value)}
                        disabled={request.status !== 'pending'}
                      />
                    </td>
                    <td>
                      <div className="stack" style={{ gap: '0.5rem' }}>
                        <button
                          className="button primary"
                          type="button"
                          onClick={() => handleDecision(request.id, 'approve')}
                          disabled={request.status !== 'pending'}
                        >
                          Одобрить
                        </button>
                        <button
                          className="button ghost"
                          type="button"
                          onClick={() => handleDecision(request.id, 'reject')}
                          disabled={request.status !== 'pending'}
                        >
                          Отклонить
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
