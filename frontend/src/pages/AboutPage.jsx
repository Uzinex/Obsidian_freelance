import HeroImage from '../assets/about-hero.svg?url';
import SeoHelmet from '../components/SeoHelmet.jsx';
import { useLocale } from '../context/LocaleContext.jsx';
import { publicContent } from '../mocks/publicContent.js';

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

const howItWorksCopy = {
  ru: [
    {
      id: 'brief',
      title: 'Бриф и скоринг',
      description: 'Уточняем цели, формируем KPI и проверяем проект на риски. Курируем бриф и оцениваем бюджет.',
    },
    {
      id: 'match',
      title: 'Подбор команды',
      description: 'В течение 48 часов выдаём shortlist специалистов и компаний с подтверждённым стеком.',
    },
    {
      id: 'kickoff',
      title: 'Запуск и спринты',
      description: 'Escrow фиксирует бюджет по этапам, а кураторы следят за сроками и качеством поставки.',
    },
    {
      id: 'review',
      title: 'Сдача и аналитика',
      description: 'Собираем отзывы, считаем фактический ROI и оптимизируем дальнейший pipeline.',
    },
  ],
  uz: [
    { id: 'brief', title: 'Brif va skoring', description: 'Maqsad va KPI ni aniqlab, loyihani risklarga tekshiramiz.' },
    { id: 'match', title: 'Komanda tanlash', description: '48 soat ichida tasdiqlangan mutaxassislar shortlistini beramiz.' },
    { id: 'kickoff', title: 'Start va sprintlar', description: 'Escrow byudjetni bosqichlarga bo‘lib, kuratorlar sifatni nazorat qiladi.' },
    { id: 'review', title: 'Qabul va analitika', description: 'Feedback yig‘amiz va ROI ni hisoblab, keyingi ishlarni rejalashtiramiz.' },
  ],
};

const monitoringPoints = {
  ru: [
    'Ежедневные отчёты о прогрессе и автоматические уведомления по SLA.',
    'Статус escrow отражается в Grafana; при отклонениях срабатывает алёрт.',
    'При нарушении KPI куратор инициирует разбор в течение 4 часов.',
  ],
  uz: [
    'Kundalik прогресс-репортlar va SLA bo‘yicha avtomatik xabarlar.',
    'Escrow statusi графанада ko‘rsatiladi, buzilish bo‘lsa — алёрт.',
    'KPI bajarilmasa, kuраторlar жалобани 4 soatda ko‘rib chiqadi.',
  ],
};

const escrowFeatures = {
  ru: [
    {
      title: 'Бюджет под защитой',
      description: 'Деньги хранятся на сегрегированном счёте банка-партнёра и разблокируются после приёмки.',
    },
    {
      title: 'Staged-платежи',
      description: 'Каждый спринт имеет свой лимит, SLA и webhooks для автоматизации.',
    },
    {
      title: 'Панель прозрачности',
      description: 'Владелец проекта видит burn-down, финансовые потоки и логи доступов.',
    },
  ],
  uz: [
    { title: 'Budjet himoyada', description: 'Pul sherik bank hisobida saqlanadi va qabuldan keyin yechiladi.' },
    { title: 'Bosqichma-bosqich to‘lov', description: 'Har bir sprintga alohida limit va SLA belgilanadi.' },
    { title: 'Shaffof panel', description: 'Buyurtmachi burn-down va moliyaviy loglarni ko‘radi.' },
  ],
};

const escrowBenefits = {
  ru: [
    'AML/KYC проверка и автоматические compliance-логи.',
    'Стратегия stale-while-revalidate для статусов в реальном времени.',
    'Наблюдаемость в Grafana и Looker Studio для анализа конверсии.',
  ],
  uz: [
    'AML/KYC tekshiruvi va avtomatik compliance loglar.',
    'Escrow статусlari uchun stale-while-revalidate strategiyasi.',
    'Grafana va Looker Studio dashboardlaridan konversiyani kuzatish.',
  ],
};

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
  const { locale } = useLocale();
  const seo = publicContent[locale].seo.about;
  const howItWorks = howItWorksCopy[locale];
  const monitoringList = monitoringPoints[locale];
  const escrow = escrowFeatures[locale];
  const escrowList = escrowBenefits[locale];

  return (
    <div className="about-page" data-analytics-id="about">
      <SeoHelmet title={seo.title} description={seo.description} path="/about" jsonLd={{ '@context': 'https://schema.org', '@type': 'Organization', name: publicContent[locale].organization.name }} />
      <section className="hero about-hero">
        <div>
          <h1>{seo.title}</h1>
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
        <img src={HeroImage} alt="Команда Obsidian" className="about-hero-illustration" loading="lazy" decoding="async" />
      </section>

      <section className="card about-stats">
        <h2>{locale === 'uz' ? 'Tasdiqlangan ekspertiza' : 'Проверенная экспертиза и измеримый эффект'}</h2>
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
        <h2>{locale === 'uz' ? 'Mijozlar bilan qanday ishlaymiz' : 'Как мы работаем с заказчиками'}</h2>
        <div className="grid three">
          {approaches.map((approach) => (
            <article key={approach.title} className="about-approach-item">
              <h3>{approach.title}</h3>
              <p>{approach.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card about-how-it-works" id="how-it-works">
        <h2>{locale === 'uz' ? 'Qanday ishlaymiz' : 'Как это работает'}</h2>
        <div className="grid two">
          {howItWorks.map((step, index) => (
            <article key={step.id} className="step-card">
              <div className="step-index">0{index + 1}</div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
        <div className="card soft" style={{ marginTop: '1.5rem' }}>
          <h3>{locale === 'uz' ? 'Monitoring va eskalatsiya' : 'Мониторинг и эскалации'}</h3>
          <ul>
            {monitoringList.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="card about-escrow" id="escrow">
        <h2>{locale === 'uz' ? 'Escrow va to‘lovlarni himoya qilish' : 'Escrow: как мы защищаем платежи'}</h2>
        <p>
          {locale === 'uz'
            ? 'Escrow orqali budjet bosqichlarga bo‘linadi, to‘lovlar esa qabuldan so‘ng yechiladi. Kuratorlar va monitoring xavfsiz va shaffof jarayonni taʼminlaydi.'
            : 'Escrow фиксирует бюджет по этапам, выплаты происходят только после приемки, а кураторы и наблюдаемость гарантируют безопасность.'}
        </p>
        <div className="grid three">
          {escrow.map((feature) => (
            <article key={feature.title} className="feature-card">
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </article>
          ))}
        </div>
        <div className="card soft" style={{ marginTop: '1.5rem' }}>
          <h3>{locale === 'uz' ? 'Escrow afzalliklari' : 'Преимущества escrow'}</h3>
          <ul>
            {escrowList.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="card timeline">
        <h2>{locale === 'uz' ? 'Qanday o‘smoqdamiz' : 'Как мы растем'}</h2>
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
        <h2>{locale === 'uz' ? 'Ekotizimga qo‘shiling' : 'Присоединяйтесь к экосистеме'}</h2>
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
