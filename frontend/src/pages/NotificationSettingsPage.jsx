import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchNotificationPreferences,
  updateNotificationPreference,
} from '../api/client.js';

const FREQUENCY_LABELS = {
  immediate: 'Сразу',
  digest_15m: 'Каждые 15 минут',
  hourly: 'Раз в час',
  daily: 'Раз в день',
};

const CATEGORY_LABELS = {
  chat: 'Чаты',
  contract: 'Контракты и споры',
  payments: 'Платежи',
  account: 'Аккаунт',
};

const CHANNEL_LABELS = {
  in_app: 'В приложении',
  email: 'E-mail',
  web_push: 'Web push',
};

export default function NotificationSettingsPage() {
  const [preferences, setPreferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(null);

  const loadPreferences = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchNotificationPreferences();
      setPreferences(data);
    } catch (err) {
      console.error('Не удалось загрузить настройки уведомлений', err);
      setError('Не удалось загрузить настройки уведомлений.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  const groupedPreferences = useMemo(() => {
    return preferences.reduce((acc, pref) => {
      if (!acc[pref.category]) acc[pref.category] = [];
      acc[pref.category].push(pref);
      return acc;
    }, {});
  }, [preferences]);

  const handleUpdate = async (id, payload) => {
    setSaving(id);
    try {
      const updated = await updateNotificationPreference(id, payload);
      setPreferences((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      console.error('Не удалось обновить настройки уведомлений', err);
      alert('Не удалось сохранить изменения.');
    } finally {
      setSaving(null);
    }
  };

  const renderPreferenceRow = (pref) => (
    <tr key={pref.id}>
      <td>
        <div className="channel-pill">{CHANNEL_LABELS[pref.channel] || pref.channel}</div>
      </td>
      <td>
        <label className="toggle">
          <input
            type="checkbox"
            checked={pref.enabled}
            onChange={(event) => handleUpdate(pref.id, { enabled: event.target.checked })}
            disabled={saving === pref.id}
          />
          <span>Включено</span>
        </label>
      </td>
      <td>
        <select
          value={pref.frequency}
          onChange={(event) => handleUpdate(pref.id, { frequency: event.target.value })}
          disabled={saving === pref.id}
        >
          {Object.entries(FREQUENCY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </td>
      <td className="quiet-hours">
        <input
          type="time"
          value={pref.quiet_hours_start || ''}
          onChange={(event) => handleUpdate(pref.id, { quiet_hours_start: event.target.value })}
          disabled={saving === pref.id}
        />
        <span>—</span>
        <input
          type="time"
          value={pref.quiet_hours_end || ''}
          onChange={(event) => handleUpdate(pref.id, { quiet_hours_end: event.target.value })}
          disabled={saving === pref.id}
        />
      </td>
      <td>
        <input
          type="number"
          min="0"
          max="23"
          value={pref.daily_digest_hour}
          onChange={(event) => handleUpdate(pref.id, { daily_digest_hour: Number(event.target.value) })}
          disabled={saving === pref.id}
        />
      </td>
      <td>
        <input
          type="text"
          value={pref.timezone}
          onChange={(event) => handleUpdate(pref.id, { timezone: event.target.value })}
          disabled={saving === pref.id}
        />
      </td>
      <td>
        <select
          value={pref.language}
          onChange={(event) => handleUpdate(pref.id, { language: event.target.value })}
          disabled={saving === pref.id}
        >
          <option value="ru">Русский</option>
          <option value="en">English</option>
        </select>
      </td>
    </tr>
  );

  return (
    <div className="page notification-settings-page">
      <header className="page-header">
        <h1>Настройки уведомлений</h1>
        <p>Управляйте каналами доставки, частотой и «тихими часами» для каждой категории событий.</p>
      </header>
      {loading ? (
        <div className="card">
          <p>Загружаем предпочтения…</p>
        </div>
      ) : error ? (
        <div className="card alert">{error}</div>
      ) : (
        Object.entries(groupedPreferences).map(([category, prefs]) => (
          <section key={category} className="card preference-card">
            <h2>{CATEGORY_LABELS[category] || category}</h2>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Канал</th>
                    <th>Статус</th>
                    <th>Частота</th>
                    <th>Тихие часы</th>
                    <th>Час дайджеста</th>
                    <th>Часовой пояс</th>
                    <th>Язык</th>
                  </tr>
                </thead>
                <tbody>{prefs.map(renderPreferenceRow)}</tbody>
              </table>
            </div>
          </section>
        ))
      )}
    </div>
  );
}
