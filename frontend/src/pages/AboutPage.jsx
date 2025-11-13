import HeroImage from '../assets/about-hero.svg?url';

const milestones = [
  {
    year: '2021',
    title: 'Запуск платформы',
    description:
      'Сформировали сообщество из первых специалистов Центральной Азии и задали стандарты прозрачной дистанционной работы.',
  },
  {
    year: '2022',
    title: 'Инфраструктура доверия',
    description:
      'Запустили эскроу-расчеты, проверку профилей и модуль оценки рисков — заказчики получают гарантированный результат.',
  },
  {
    year: '2023',
    title: 'Интеллектуальный подбор',
    description:
      'Алгоритмы и ручной ресерч помогают формировать проектные команды под задачи любой сложности.',
  },
  {
    year: '2024',
    title: 'Масштабирование международных проектов',
    description:
      'Развернули сопровождение для корпоративных клиентов и вышли на рынки Ближнего Востока и Европы.',
  },
];

const values = [
  {
    title: 'Партнерство',
    description:
      'Мы работаем в формате консалтинга: помогаем сформулировать задачу, подобрать команду и сопровождаем проект до результата.',
  },
  {
    title: 'Ответственность',
    description:
      'Формализованные процессы, compliance-проверки и прозрачная отчетность на каждом этапе сотрудничества.',
  },
  {
    title: 'Качество',
    description:
      'Эксперты проходят многоуровневый отбор, а внутренние методологи контролируют качество и сроки выполнения работ.',
  },
  {
    title: 'Рост экосистемы',
    description:
      'Инвестируем в развитие рынка: образовательные программы, карьерные треки, менторство и отраслевые ивенты.',
  },
];

const stats = [
  { value: '500+', label: 'Проверенных специалистов в активном пуле' },
  { value: '120', label: 'Компаний-резидентов, ведущих проекты через платформу' },
  { value: '94%', label: 'Проектов завершаются в срок и с оценкой “выше ожиданий”' },
  { value: '48 часов', label: 'Среднее время на подбор команды под задачу' },
];

const approaches = [
  {
    title: 'Стратегическая экспертиза',
    description:
      'Работаем с бэкграундом индустрии клиента, формируем продуктовые гипотезы и управляем дорожной картой проекта.',
  },
  {
    title: 'Технологический продакшн',
    description:
      'Комплектуем команду специалистами по разработке, дизайну и аналитике, интегрируемся в процессы заказчика и берем на себя delivery.',
  },
  {
    title: 'Операционная поддержка',
    description:
      'Обеспечиваем юридическое оформление, финансовые расчеты, контроль качества и круглосуточный сервис-менеджмент.',
  },
];

export default function AboutPage() {
  return (
    <div className="about-page">
      <section className="hero about-hero">
        <div>
          <h1>О платформе Obsidian Freelance</h1>
          <p>
            Obsidian Freelance — цифровой партнер для бизнеса, которому нужны точные проектные решения и управляемый доступ к
            экспертам. Мы соединяем компании и специалистов, выстраиваем процессы и обеспечиваем контроль качества, чтобы
            каждая инициатива завершалась прогнозируемым результатом.
          </p>
          <p>
            Наша команда сочетает опыт продуктовых студий, консалтингов и техподдержки. Благодаря этому мы создаем экосистему,
            где фриланс перестает быть риском и становится инструментом роста.
          </p>
        </div>
        <img src={HeroImage} alt="Команда Obsidian" className="about-hero-illustration" />
      </section>

      <section className="card about-stats">
        <h2>Проверенная экспертиза и измеримый эффект</h2>
        <div className="grid four">
          {stats.map((stat) => (
            <div key={stat.label} className="about-stat">
              <span className="about-stat-value">{stat.value}</span>
              <span className="about-stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="grid two">
        {values.map((value) => (
          <article key={value.title} className="card soft">
            <h2>{value.title}</h2>
            <p>{value.description}</p>
          </article>
        ))}
      </section>

      <section className="card about-approach">
        <h2>Как мы работаем с заказчиками</h2>
        <div className="grid three">
          {approaches.map((approach) => (
            <article key={approach.title} className="about-approach-item">
              <h3>{approach.title}</h3>
              <p>{approach.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card timeline">
        <h2>Как мы растем</h2>
        <div className="timeline-track">
          {milestones.map((milestone) => (
            <div key={milestone.year} className="timeline-item">
              <div className="timeline-year">{milestone.year}</div>
              <div>
                <h3>{milestone.title}</h3>
                <p>{milestone.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card about-cta">
        <h2>Присоединяйтесь к экосистеме</h2>
        <p>
          Независимо от масштаба задачи, вы получаете прозрачную архитектуру взаимодействия: единый договор, защищенные расчеты,
          измеримую отчетность и сервис-менеджера, который отвечает за успех проекта.
        </p>
        <ul>
          <li>Бизнесу — ускоряем выход продукта на рынок и отвечаем за результат вместе с вами.</li>
          <li>Экспертам — предоставляем стабильный поток релевантных задач, развитие и поддержку сообщества.</li>
          <li>Партнерам — объединяемся ради комплексных решений, сохраняя единые стандарты качества.</li>
        </ul>
      </section>
    </div>
  );
}
