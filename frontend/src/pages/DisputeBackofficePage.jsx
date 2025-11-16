import { useEffect, useMemo, useState } from 'react';
import {
  executeDisputeOutcome,
  fetchDisputeCase,
  fetchDisputeCases,
  updateDisputeStatus,
  uploadDisputeEvidence,
} from '../api/client.js';
import { formatDateTime } from '../utils/formatting.js';

const STATUS_CHOICES = [
  { value: '', label: 'Все' },
  { value: 'opened', label: 'Открыт' },
  { value: 'evidence_needed', label: 'Нужны доказательства' },
  { value: 'in_review', label: 'На рассмотрении' },
  { value: 'resolution_proposed', label: 'Предложено решение' },
  { value: 'resolved', label: 'Закрыт' },
];

const OUTCOME_CHOICES = [
  { value: 'full_release', label: 'Full release' },
  { value: 'partial_release', label: 'Partial release' },
  { value: 'refund', label: 'Refund' },
];

export default function DisputeBackofficePage() {
  const [cases, setCases] = useState([]);
  const [filters, setFilters] = useState({ status: '', priority: '', overdue: '', min_amount: '', max_amount: '' });
  const [selectedId, setSelectedId] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusValue, setStatusValue] = useState('in_review');
  const [outcomeValue, setOutcomeValue] = useState('full_release');
  const [outcomePayload, setOutcomePayload] = useState('{}');
  const [linkEvidence, setLinkEvidence] = useState({ title: '', link: '' });

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await fetchDisputeCases(filters);
        setCases(data.results ?? data);
      } catch (err) {
        console.error('Failed to load disputes', err);
        setError('Не удалось загрузить список споров');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [filters]);

  useEffect(() => {
    if (!selectedId) {
      setSelectedCase(null);
      return;
    }
    async function loadCase() {
      try {
        const detail = await fetchDisputeCase(selectedId);
        setSelectedCase(detail);
      } catch (err) {
        console.error('Failed to load dispute case', err);
        setError('Не удалось загрузить карточку спора');
      }
    }
    loadCase();
  }, [selectedId]);

  const formattedEvents = useMemo(() => {
    if (!selectedCase?.events) return [];
    return selectedCase.events.map((event) => ({ ...event, created_at: formatDateTime(event.created_at) }));
  }, [selectedCase]);

  const handleStatusUpdate = async () => {
    if (!selectedCase) return;
    try {
      const updated = await updateDisputeStatus(selectedCase.id, { status: statusValue });
      setSelectedCase(updated);
      setCases((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      console.error('Failed to update dispute status', err);
      setError('Не удалось обновить статус спора');
    }
  };

  const handleOutcome = async () => {
    if (!selectedCase) return;
    try {
      let parsed = {};
      try {
        parsed = JSON.parse(outcomePayload || '{}');
      } catch (err) {
        setError('Payload должен быть в формате JSON');
        return;
      }
      const updatedOutcome = await executeDisputeOutcome(selectedCase.id, { outcome: outcomeValue, payload: parsed });
      setSelectedCase((prev) => ({ ...prev, outcome: updatedOutcome, status: 'resolved' }));
    } catch (err) {
      console.error('Failed to execute outcome', err);
      setError('Не удалось применить исход по эскроу');
    }
  };

  const handleEvidenceUpload = async (event) => {
    if (!selectedCase) return;
    const file = event.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const evidence = await uploadDisputeEvidence(selectedCase.id, formData);
      setSelectedCase((prev) => ({ ...prev, evidence: [...(prev?.evidence || []), evidence] }));
    } catch (err) {
      console.error('Failed to upload evidence', err);
      setError('Не удалось загрузить доказательство');
    }
  };

  const handleLinkEvidence = async () => {
    if (!selectedCase || !linkEvidence.link) return;
    const formData = new FormData();
    formData.append('link_url', linkEvidence.link);
    if (linkEvidence.title) formData.append('title', linkEvidence.title);
    try {
      const evidence = await uploadDisputeEvidence(selectedCase.id, formData);
      setSelectedCase((prev) => ({ ...prev, evidence: [...(prev?.evidence || []), evidence] }));
      setLinkEvidence({ title: '', link: '' });
    } catch (err) {
      console.error('Failed to upload link evidence', err);
      setError('Не удалось сохранить ссылку');
    }
  };

  return (
    <section className="card dispute-backoffice">
      <header>
        <h1>Арбитражные кейсы</h1>
        <p className="muted">Финансовые и модераторские команды работают в одной очереди</p>
      </header>
      <div className="filters-grid">
        <label>
          Статус
          <select value={filters.status} onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}>
            {STATUS_CHOICES.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
        <label>
          Мин. сумма
          <input type="number" value={filters.min_amount} onChange={(event) => setFilters((prev) => ({ ...prev, min_amount: event.target.value }))} />
        </label>
        <label>
          Макс. сумма
          <input type="number" value={filters.max_amount} onChange={(event) => setFilters((prev) => ({ ...prev, max_amount: event.target.value }))} />
        </label>
        <label>
          Просрочки
          <select value={filters.overdue} onChange={(event) => setFilters((prev) => ({ ...prev, overdue: event.target.value }))}>
            <option value="">Все</option>
            <option value="true">Просроченные</option>
          </select>
        </label>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <div className="dispute-list">
          {cases.map((item) => (
            <article key={item.id} className={`dispute-card status-${item.status}`} onClick={() => setSelectedId(item.id)}>
              <header>
                <h3>Спор #{item.id}</h3>
                <span className="badge">{item.status}</span>
              </header>
              <p>Контракт #{item.contract_id}</p>
              <p>Категория: {item.category || '—'}</p>
              <p>Сумма: {item.amount_under_review}</p>
              <p>SLA: {formatDateTime(item.sla_due_at)}</p>
            </article>
          ))}
        </div>
      )}
      {selectedCase && (
        <section className="card dispute-detail">
          <header>
            <h2>Спор #{selectedCase.id}</h2>
            <p>Статус: {selectedCase.status}</p>
          </header>
          <div className="two-column">
            <div>
              <h3>Участники</h3>
              <ul>
                {selectedCase.participants?.map((participant) => (
                  <li key={`${participant.role}-${participant.profile_id}`}>
                    {participant.role} · Профиль #{participant.profile_id}
                  </li>
                ))}
              </ul>
              <h3>Доказательства</h3>
              <ul>
                {selectedCase.evidence?.map((item) => (
                  <li key={item.id}>{item.title || item.kind} — {item.link_url || 'файл'}</li>
                ))}
              </ul>
              <div className="upload-block">
                <label>
                  Загрузить файл
                  <input type="file" onChange={handleEvidenceUpload} />
                </label>
                <div className="link-upload">
                  <input type="text" placeholder="Название" value={linkEvidence.title} onChange={(event) => setLinkEvidence((prev) => ({ ...prev, title: event.target.value }))} />
                  <input type="url" placeholder="Ссылка" value={linkEvidence.link} onChange={(event) => setLinkEvidence((prev) => ({ ...prev, link: event.target.value }))} />
                  <button type="button" onClick={handleLinkEvidence}>Добавить ссылку</button>
                </div>
              </div>
            </div>
            <div>
              <h3>Лента событий</h3>
              <ol className="timeline">
                {formattedEvents.map((event, index) => (
                  <li key={`${event.type}-${index}`}>
                    <strong>{event.type}</strong>
                    <p>{event.payload?.status || event.payload?.note || JSON.stringify(event.payload)}</p>
                    <span className="muted">{event.created_at}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
          <div className="action-row">
            <div>
              <h4>Обновить статус</h4>
              <select value={statusValue} onChange={(event) => setStatusValue(event.target.value)}>
                {STATUS_CHOICES.filter((option) => option.value).map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <button type="button" onClick={handleStatusUpdate}>Сохранить статус</button>
            </div>
            <div>
              <h4>Исход по эскроу</h4>
              <select value={outcomeValue} onChange={(event) => setOutcomeValue(event.target.value)}>
                {OUTCOME_CHOICES.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <textarea value={outcomePayload} onChange={(event) => setOutcomePayload(event.target.value)} placeholder='{"client_share": 0.5}'>
              </textarea>
              <button type="button" className="primary" onClick={handleOutcome}>Подтвердить исход</button>
            </div>
          </div>
        </section>
      )}
    </section>
  );
}
