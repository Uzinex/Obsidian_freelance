const automationFeatures = [
  {
    title: 'Автопоиск специалистов',
    description: 'Роботы анализируют проект и предлагают подходящих исполнителей с учетом компетенций и рейтинга.',
  },
  {
    title: 'Автоматические дедлайны',
    description: 'Платформа следит за этапами проекта и напоминает команде о ключевых сроках и документах.',
  },
  {
    title: 'Мониторинг качества',
    description: 'Система оценивает прогресс по чек-листам и собирает обратную связь, чтобы проект завершился вовремя.',
  },
];

const assistants = [
  {
    name: 'Onyx',
    role: 'Помощник по запуску проектов',
    description: 'Собирает бриф, предлагает структуру команды и запускает закупку услуг за 10 минут.',
  },
  {
    name: 'Graphite',
    role: 'Финансовый контроллер',
    description: 'Формирует сметы, резервирует бюджет и автоматически готовит акты и счета.',
  },
  {
    name: 'Quartz',
    role: 'Куратор качества',
    description: 'Отслеживает чек-пойнты, собирает ревью и помогает поддерживать высокий уровень сервиса.',
  },
];

export default function RobotsPage() {
  return (
    <div className="robots-page">
      <section className="hero robots-hero">
        <h1>Роботы-ассистенты для заказчиков</h1>
        <p>
          Команда цифровых ассистентов помогает вам управлять проектами: от подбора исполнителей до контроля бюджета
          и качества. Вы фокусируетесь на стратегии, роботы — на операционке.
        </p>
      </section>

      <section className="grid three">
        {automationFeatures.map((feature) => (
          <article key={feature.title} className="card soft">
            <h2>{feature.title}</h2>
            <p>{feature.description}</p>
          </article>
        ))}
      </section>

      <section className="card assistants">
        <h2>Ассистенты Obsidian</h2>
        <div className="grid three">
          {assistants.map((assistant) => (
            <article key={assistant.name} className="assistant-card">
              <div className="assistant-avatar" aria-hidden="true">
                {assistant.name.charAt(0)}
              </div>
              <h3>{assistant.name}</h3>
              <p className="assistant-role">{assistant.role}</p>
              <p>{assistant.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card about-cta">
        <h2>Запустить проект с роботами легко</h2>
        <ol>
          <li>Опишите цель и бюджет — Onyx подготовит бриф.</li>
          <li>Выберите предложенную команду или скорректируйте ее.</li>
          <li>Получайте отчеты и уведомления, пока ассистенты управляют процессом.</li>
        </ol>
        <p>Готовы попробовать? Создайте заказ и подключите цифровых помощников в личном кабинете.</p>
      </section>
    </div>
  );
}
