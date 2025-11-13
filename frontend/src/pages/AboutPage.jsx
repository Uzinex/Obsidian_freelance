import HeroImage from '../assets/about-hero.svg?url';

const milestones = [
  {
    year: '2021',
    title: 'Запуск платформы',
    description:
      'Мы объединили первые сотни специалистов из Узбекистана и ближних стран, чтобы показать, что удаленная работа может быть прозрачной и надежной.',
  },
  {
    year: '2022',
    title: 'Гарантированный безопасный расчет',
    description:
      'Внедрили защищенные эскроу-платежи и программу проверки исполнителей, чтобы заказчики были уверены в результате.',
  },
  {
    year: '2023',
    title: 'Умные рекомендации',
    description:
      'Алгоритмы подбирают проекты по навыкам и опыту, экономя время и для заказчиков, и для фрилансеров.',
  },
];

const values = [
  {
    title: 'Прозрачность',
    description: 'Каждый шаг сделки фиксируется: от первой заявки до закрытия проекта и выплат.',
  },
  {
    title: 'Поддержка',
    description: 'Команда кураторов помогает решить вопросы по проектам и развитию специалиста.',
  },
  {
    title: 'Рост',
    description: 'Мы инвестируем в сообщество: образовательные программы, вебинары и менторство.',
  },
];

export default function AboutPage() {
  return (
    <div className="about-page">
      <section className="hero about-hero">
        <div>
          <h1>О платформе Obsidian Freelance</h1>
          <p>
            Мы строим цифровую экосистему, которая помогает компаниям запускать проекты быстрее, а специалистам —
            работать на международном уровне. Наша цель — сделать профессиональные услуги доступными и понятными.
          </p>
        </div>
        <img src={HeroImage} alt="Команда Obsidian" className="about-hero-illustration" />
      </section>

      <section className="grid two">
        {values.map((value) => (
          <article key={value.title} className="card soft">
            <h2>{value.title}</h2>
            <p>{value.description}</p>
          </article>
        ))}
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
          Вне зависимости от роли вы получаете инструменты для прозрачной работы: защищенные платежи, систему
          отзывов, аналитические отчеты и поддержку кураторов.
        </p>
        <ul>
          <li>Заказчики — создавайте команды за несколько минут.</li>
          <li>Фрилансеры — находите проекты, которые соответствуют вашим навыкам и ценностям.</li>
          <li>Компании — собирайте распределенные команды и масштабируйтесь без риска.</li>
        </ul>
      </section>
    </div>
  );
}
