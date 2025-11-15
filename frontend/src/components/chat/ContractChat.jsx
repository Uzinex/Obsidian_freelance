import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

const STATUS_LABELS = {
  sent: { icon: '✓', label: 'Отправлено' },
  delivered: { icon: '✓✓', label: 'Доставлено' },
  read: { icon: '✓✓', label: 'Прочитано', emphasis: true },
  pending: { icon: '…', label: 'В очереди' },
};

const QUICK_ACTIONS = [
  { id: 'propose_milestone', label: 'Предложить milestone' },
  { id: 'request_revision', label: 'Запросить правки' },
  { id: 'open_dispute', label: 'Открыть спор' },
];

const REPORT_CATEGORIES = [
  { id: 'fraud', label: 'Мошенничество' },
  { id: 'banned_payment', label: 'Запрещённые реквизиты' },
  { id: 'abuse', label: 'Оскорбления' },
  { id: 'spam', label: 'Спам/реклама' },
];

const QUICK_ACTION_LABELS = QUICK_ACTIONS.reduce((acc, action) => {
  acc[action.id] = action.label;
  return acc;
}, {});

const EMPTY_STATE = {
  idle: 'Нет сообщений',
  offline: 'Потеряно соединение',
  sending: 'Идёт отправка…',
};

const queueId = () => (window.crypto?.randomUUID ? window.crypto.randomUUID() : `${Date.now()}-${Math.random()}`);

export default function ContractChat({
  contractId,
  authToken,
  apiBaseUrl = '/api/chat',
  wsBaseUrl = `ws://${window.location.host}/ws/chat`,
  presenceEnabled = false,
  currentUserId,
}) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [connectionState, setConnectionState] = useState('connecting');
  const [typingState, setTypingState] = useState(null);
  const [queue, setQueue] = useState([]);
  const socketRef = useRef(null);
  const cursorRef = useRef(null);
  const [error, setError] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);
  const [reportingMessageId, setReportingMessageId] = useState(null);
  const [reportCategory, setReportCategory] = useState(REPORT_CATEGORIES[0].id);
  const [reportComment, setReportComment] = useState('');
  const [reportSuccess, setReportSuccess] = useState('');

  const authHeaders = useMemo(() => ({
    Authorization: authToken ? `Bearer ${authToken}` : undefined,
  }), [authToken]);

  const fetchJson = useCallback(async (path, options = {}) => {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(authHeaders.Authorization ? { Authorization: authHeaders.Authorization } : {}),
        ...options.headers,
      },
      credentials: 'include',
      ...options,
    });
    if (!response.ok) {
      throw new Error(`Chat API error: ${response.status}`);
    }
    return response.json();
  }, [apiBaseUrl, authHeaders]);

  useEffect(() => {
    async function bootstrap() {
      try {
        const data = await fetchJson(`/contracts/${contractId}/messages/?page_size=50`);
        setMessages(data.results ?? data);
        cursorRef.current = new Date().toISOString();
      } catch (err) {
        console.error('Failed to bootstrap chat', err);
        setError('Не удалось загрузить чат');
      }
    }
    bootstrap();
  }, [contractId, fetchJson]);

  const flushQueue = useCallback(() => {
    if (connectionState !== 'online' || !queue.length) return;
    setQueue((items) => {
      items.forEach((item) => {
        socketRef.current?.send(JSON.stringify({ action: 'send_message', payload: item }));
      });
      return [];
    });
  }, [connectionState, queue.length]);

  const openSocket = useCallback(() => {
    const wsUrl = `${wsBaseUrl}/contracts/${contractId}/?token=${encodeURIComponent(authToken ?? '')}`;
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;
    socket.addEventListener('open', () => {
      setConnectionState('online');
      setError(null);
      flushQueue();
    });
    socket.addEventListener('close', () => {
      setConnectionState('offline');
    });
    socket.addEventListener('error', () => {
      setConnectionState('offline');
    });
    socket.addEventListener('message', (event) => {
      try {
        const payload = JSON.parse(event.data);
        handleSocketEvent(payload);
      } catch (err) {
        console.warn('Unable to parse WebSocket payload', err);
      }
    });
  }, [authToken, contractId, wsBaseUrl, flushQueue]);

  useEffect(() => {
    openSocket();
    return () => {
      socketRef.current?.close();
    };
  }, [openSocket]);

  const handleSocketEvent = useCallback((payload) => {
    if (payload.type === 'message') {
      setMessages((current) => mergeMessages(current, payload.payload));
      cursorRef.current = new Date().toISOString();
    } else if (payload.type === 'status') {
      setMessages((current) => current.map((message) => (
        message.id === payload.payload.id
          ? { ...message, status: payload.payload.status, delivered_at: payload.payload.delivered_at, read_at: payload.payload.read_at }
          : message
      )));
    } else if (payload.type === 'presence' && presenceEnabled) {
      setTypingState(() => (payload.payload.status === 'online' ? null : 'Собеседник оффлайн'));
    } else if (payload.type === 'typing' && presenceEnabled) {
      setTypingState(() => (payload.payload.state === 'typing' ? 'Собеседник печатает…' : null));
    }
  }, [presenceEnabled]);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (connectionState === 'online') return;
      if (!cursorRef.current) return;
      try {
        const events = await fetchJson(`/contracts/${contractId}/events/?since=${cursorRef.current}`);
        events.events?.forEach(handleSocketEvent);
        cursorRef.current = events.next_cursor;
      } catch (err) {
        console.warn('Polling failed', err);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [connectionState, contractId, fetchJson, handleSocketEvent]);

  const dispatchPayload = useCallback((payload, localAttachments = []) => {
    const command = { action: 'send_message', payload };
    if (connectionState === 'online') {
      socketRef.current?.send(JSON.stringify(command));
    } else {
      const fallbackBody = payload.body || QUICK_ACTION_LABELS[payload.action] || '';
      const localMessage = {
        id: queueId(),
        body: fallbackBody,
        status: 'pending',
        sent_at: new Date().toISOString(),
        attachments: localAttachments,
        action: payload.action,
        isLocal: true,
      };
      setMessages((current) => [...current, localMessage]);
      setQueue((items) => [...items, payload]);
    }
  }, [connectionState]);

  const sendMessage = useCallback(async () => {
    if (!inputValue.trim() && attachments.length === 0) return;
    const attachmentIds = attachments.map((item) => item.id);
    const payload = { body: inputValue.trim(), attachments: attachmentIds };
    const localAttachments = attachments.map((item) => ({ ...item }));
    setInputValue('');
    setAttachments([]);
    dispatchPayload(payload, localAttachments);
  }, [attachments, dispatchPayload, inputValue]);

  const sendQuickAction = (actionId) => {
    dispatchPayload({ action: actionId, body: QUICK_ACTION_LABELS[actionId], attachments: [] });
  };

  const onKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${apiBaseUrl}/contracts/${contractId}/attachments/`, {
        method: 'POST',
        body: formData,
        headers: {
          ...(authHeaders.Authorization ? { Authorization: authHeaders.Authorization } : {}),
        },
        credentials: 'include',
      });
      if (!response.ok) throw new Error('upload failed');
      const data = await response.json();
      setAttachments((prev) => [...prev, data]);
    } catch (err) {
      console.error('Attachment upload failed', err);
      setError('Вложение не загружено');
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const downloadAttachment = async (attachmentId) => {
    try {
      const data = await fetchJson(`/contracts/${contractId}/attachments/${attachmentId}/presign/`, { method: 'POST' });
      window.open(data.url, '_blank', 'noopener');
    } catch (err) {
      console.error('Failed to presign attachment', err);
      setError('Не удалось открыть вложение');
    }
  };

  const submitReport = async (messageId) => {
    try {
      await fetchJson(`/contracts/${contractId}/messages/${messageId}/reports/`, {
        method: 'POST',
        body: JSON.stringify({ category: reportCategory, comment: reportComment }),
      });
      setReportSuccess('Жалоба отправлена модераторам');
      setReportingMessageId(null);
      setReportComment('');
    } catch (err) {
      console.error('Failed to submit report', err);
      setError('Не удалось отправить жалобу');
    }
  };

  const emptyStateLabel = useMemo(() => {
    if (messages.length === 0) {
      if (connectionState === 'offline') return EMPTY_STATE.offline;
      if (queue.length > 0) return EMPTY_STATE.sending;
      return EMPTY_STATE.idle;
    }
    if (queue.length > 0 && connectionState !== 'online') {
      return EMPTY_STATE.sending;
    }
    return null;
  }, [connectionState, messages.length, queue.length]);

  return (
    <section className="contract-chat" aria-live="polite">
      <header className="chat-header">
        <div>
          <p className="chat-title">Чат контракта #{contractId}</p>
          <p className={`chat-status chat-status-${connectionState}`} aria-live="polite">
            {connectionState === 'online' ? 'Онлайн' : 'Оффлайн'}
          </p>
        </div>
        {typingState && <p className="chat-typing" aria-live="polite">{typingState}</p>}
      </header>
      <div className="chat-messages" role="log" aria-live="polite" aria-busy={connectionState === 'connecting'}>
        {emptyStateLabel && <p className="chat-empty-state">{emptyStateLabel}</p>}
        {messages.map((message) => {
          const isOwnMessage = currentUserId && message.sender_id === currentUserId;
          return (
            <article key={message.id} className={`chat-message ${message.sender_id ? '' : 'chat-message-system'}`} tabIndex={0}>
              <p className="chat-message-body">{message.body}</p>
            {message.attachments?.length > 0 && (
              <ul className="chat-attachments" aria-label="Вложения">
                {message.attachments.map((attachment) => (
                  <li key={attachment.id}>
                    <button type="button" onClick={() => downloadAttachment(attachment.id)}>
                      {attachment.original_name} ({attachment.mime_type})
                    </button>
                  </li>
                ))}
              </ul>
            )}
            {STATUS_LABELS[message.status] && (
              <span className={`chat-message-status ${STATUS_LABELS[message.status].emphasis ? 'chat-message-status-read' : ''}`}>
                {STATUS_LABELS[message.status].icon} {STATUS_LABELS[message.status].label}
              </span>
            )}
              {!isOwnMessage && message.sender_id && (
                <button type="button" className="report-link" onClick={() => {
                  setReportingMessageId(message.id);
                  setReportCategory(REPORT_CATEGORIES[0].id);
                  setReportComment('');
                }}>
                  Пожаловаться
                </button>
              )}
              {reportingMessageId === message.id && (
                <form className="report-form" onSubmit={(event) => { event.preventDefault(); submitReport(message.id); }}>
                  <label>
                    Категория
                    <select value={reportCategory} onChange={(event) => setReportCategory(event.target.value)}>
                      {REPORT_CATEGORIES.map((category) => (
                        <option key={category.id} value={category.id}>{category.label}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Комментарий
                    <textarea value={reportComment} onChange={(event) => setReportComment(event.target.value)} placeholder="Опишите нарушение" />
                  </label>
                  <div className="report-actions">
                    <button type="submit" className="primary">Отправить</button>
                    <button type="button" onClick={() => setReportingMessageId(null)}>Отмена</button>
                  </div>
                </form>
              )}
          </article>
          );
        })}
      </div>
      <footer className="chat-composer">
        {error && <p className="chat-error" role="alert">{error}</p>}
        {reportSuccess && <p className="chat-success" role="status">{reportSuccess}</p>}
        <div className="chat-quick-actions" role="group" aria-label="Быстрые действия">
          {QUICK_ACTIONS.map((action) => (
            <button key={action.id} type="button" onClick={() => sendQuickAction(action.id)}>
              {action.label}
            </button>
          ))}
        </div>
        <div className="chat-input-group">
          <textarea
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={onKeyPress}
            aria-label="Введите сообщение"
            placeholder="Напишите сообщение"
          />
          <div className="chat-input-actions">
            <input type="file" ref={fileInputRef} onChange={handleFileChange} aria-label="Прикрепить файл" />
            <button type="button" onClick={sendMessage} aria-label="Отправить сообщение" disabled={!inputValue && attachments.length === 0}>
              Отправить
            </button>
          </div>
        </div>
        {attachments.length > 0 && (
          <ul className="chat-attachment-preview" aria-label="Предпросмотр вложений">
            {attachments.map((item) => (
              <li key={item.id}>{item.original_name}</li>
            ))}
          </ul>
        )}
      </footer>
    </section>
  );
}

function mergeMessages(existing, incoming) {
  const found = existing.some((message) => message.id === incoming.id);
  if (found) {
    return existing.map((message) => (message.id === incoming.id ? { ...message, ...incoming } : message));
  }
  return [...existing, incoming];
}
