import { useEffect, useState } from 'react';
import { fetchModerationCases, updateModerationCase } from '../api/client.js';

const STATUS_OPTIONS = [
  { value: '', label: 'Все' },
  { value: 'open', label: 'Открытые' },
  { value: 'in_review', label: 'В работе' },
  { value: 'resolved', label: 'Закрытые' },
];

const PRIORITY_OPTIONS = [
  { value: '', label: 'Любой приоритет' },
  { value: 'high', label: 'Высокий' },
  { value: 'medium', label: 'Средний' },
  { value: 'low', label: 'Низкий' },
];

const CATEGORY_OPTIONS = [
  { value: '', label: 'Все категории' },
  { value: 'fraud', label: 'Мошенничество' },
  { value: 'banned_payment', label: 'Запрещённые реквизиты' },
  { value: 'abuse', label: 'Оскорбления' },
  { value: 'spam', label: 'Спам' },
];

export default function ModerationQueuePage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ status: '', priority: '', category: '', overdue: '' });
  const [selectedCase, setSelectedCase] = useState(null);
  const [resolutionNotes, setResolutionNotes] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await fetchModerationCases(filters);
        setCases(data.results ?? data);
      } catch (err) {
        console.error('Failed to load moderation queue', err);
        setError('Не удалось загрузить очередь модерации');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [filters]);

  const handleStatusChange = async (caseId, status) => {
    try {
      const updated = await updateModerationCase(caseId, { status, resolution_notes: resolutionNotes });
      setCases((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setResolutionNotes('');
      setSelectedCase(updated);
    } catch (err) {
      console.error('Failed to update case', err);
      setError('Не удалось обновить статус кейса');
    }
  };

  return (
    <section className="card moderation-queue">
      <header>
        <h1>Очередь модерации чатов</h1>
        <p className="muted">Фильтры по SLA и категориям помогают приоритезировать работу</p>
      </header>
      <div className="filters-grid">
        <label>
          Статус
          <select value={filters.status} onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
        <label>
          Приоритет
          <select value={filters.priority} onChange={(event) => setFilters((prev) => ({ ...prev, priority: event.target.value }))}>
            {PRIORITY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
        <label>
          Категория
          <select value={filters.category} onChange={(event) => setFilters((prev) => ({ ...prev, category: event.target.value }))}>
            {CATEGORY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
        <label>
          Просрочки
          <select value={filters.overdue} onChange={(event) => setFilters((prev) => ({ ...prev, overdue: event.target.value }))}>
            <option value="">Все</option>
            <option value="true">Только просроченные</option>
          </select>
        </label>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="moderation-case-grid">
          {cases.map((item) => (
            <article key={item.id} className={`moderation-card priority-${item.priority}`}>
              <header>
                <p>Кейс #{item.id}</p>
                <span className="badge">{item.priority}</span>
              </header>
              <p className="muted">Причина: {item.escalation_reason}</p>
              <p>Статус: {item.status}</p>
              <p>SLA: {new Date(item.sla_due_at).toLocaleString()}</p>
              <button type="button" onClick={() => setSelectedCase(item)}>Открыть</button>
            </article>
          ))}
        </div>
      )}
      {selectedCase && (
        <section className="card moderation-case-detail">
          <header>
            <h2>Сообщение #{selectedCase.message.id}</h2>
            <p>{selectedCase.message.body || selectedCase.message.action}</p>
          </header>
          <p>Статус: {selectedCase.status}</p>
          <p>Последнее обновление: {new Date(selectedCase.escalated_at).toLocaleString()}</p>
          <label>
            Комментарий
            <textarea value={resolutionNotes} onChange={(event) => setResolutionNotes(event.target.value)} placeholder="Примечание для журнала" />
          </label>
          <div className="action-row">
            <button type="button" onClick={() => handleStatusChange(selectedCase.id, 'in_review')}>В работу</button>
            <button type="button" onClick={() => handleStatusChange(selectedCase.id, 'resolved')} className="primary">Закрыть</button>
          </div>
        </section>
      )}
    </section>
  );
}
