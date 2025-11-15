import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  fetchNotificationEvents,
  markNotificationRead,
  markAllNotificationsRead,
} from '../../api/client.js';

const CATEGORY_LABELS = {
  chat: 'Чаты',
  contract: 'Контракты',
  payments: 'Платежи',
  account: 'Аккаунт',
};

const CHANNEL_LABELS = {
  in_app: 'В приложении',
  email: 'E-mail',
  web_push: 'Web push',
};

export default function NotificationCenter() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ category: 'all', channel: 'all', unreadOnly: false });
  const [error, setError] = useState('');

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchNotificationEvents();
      setNotifications(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Не удалось загрузить уведомления', err);
      setError('Не удалось загрузить уведомления');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const filteredNotifications = useMemo(() => {
    return notifications.filter((item) => {
      if (filters.category !== 'all' && item.category !== filters.category) {
        return false;
      }
      if (filters.channel !== 'all' && !item.channels?.includes(filters.channel)) {
        return false;
      }
      if (filters.unreadOnly && item.is_read) {
        return false;
      }
      return true;
    });
  }, [notifications, filters]);

  const handleMarkRead = async (notificationId) => {
    try {
      await markNotificationRead(notificationId);
      setNotifications((prev) =>
        prev.map((item) =>
          item.id === notificationId ? { ...item, is_read: true, read_at: new Date().toISOString() } : item,
        ),
      );
    } catch (err) {
      console.error('Не удалось обновить уведомление', err);
    }
  };

  const handleMarkAll = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((item) => ({ ...item, is_read: true, read_at: new Date().toISOString() })));
    } catch (err) {
      console.error('Не удалось отметить все уведомления прочитанными', err);
    }
  };

  return (
    <div className="notification-center">
      <header className="notification-center__header">
        <div>
          <h3>Центр уведомлений</h3>
          <p className="muted-text">Лента событий с поддержкой фильтров и массовых действий.</p>
        </div>
        <div className="notification-center__actions">
          <button className="button ghost" type="button" onClick={loadNotifications} disabled={loading}>
            Обновить
          </button>
          <button className="button secondary" type="button" onClick={handleMarkAll} disabled={loading}>
            Отметить все прочитанными
          </button>
        </div>
      </header>
      <section className="notification-filters">
        <label>
          Категория
          <select
            value={filters.category}
            onChange={(event) => setFilters((prev) => ({ ...prev, category: event.target.value }))}
          >
            <option value="all">Все</option>
            {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Канал
          <select
            value={filters.channel}
            onChange={(event) => setFilters((prev) => ({ ...prev, channel: event.target.value }))}
          >
            <option value="all">Любой</option>
            {Object.entries(CHANNEL_LABELS).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={filters.unreadOnly}
            onChange={(event) => setFilters((prev) => ({ ...prev, unreadOnly: event.target.checked }))}
          />
          Показывать только непрочитанные
        </label>
      </section>
      {error ? <div className="alert error">{error}</div> : null}
      {loading ? (
        <div className="notification-empty">Загружаем уведомления…</div>
      ) : filteredNotifications.length === 0 ? (
        <div className="notification-empty">Уведомлений по заданным фильтрам пока нет.</div>
      ) : (
        <ul className="notification-list">
          {filteredNotifications.map((item) => (
            <li key={item.id} className={item.is_read ? '' : 'unread'}>
              <div className="notification-list__meta">
                <span className="badge">{CATEGORY_LABELS[item.category] || item.category}</span>
                <span className="notification-list__channels">
                  {item.channels?.map((channel) => (
                    <span className="chip" key={channel}>
                      {CHANNEL_LABELS[channel] || channel}
                    </span>
                  ))}
                </span>
                <span className="notification-list__time">
                  {new Date(item.created_at).toLocaleString('ru-RU', { hour12: false })}
                </span>
              </div>
              <h4>{item.title}</h4>
              <p>{item.message}</p>
              {item.data?.contract_id ? (
                <p className="muted-text">Контракт #{item.data.contract_id}</p>
              ) : null}
              <div className="notification-list__actions">
                {!item.is_read ? (
                  <button className="button ghost" type="button" onClick={() => handleMarkRead(item.id)}>
                    Отметить прочитанным
                  </button>
                ) : (
                  <span className="muted-text">Прочитано</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
