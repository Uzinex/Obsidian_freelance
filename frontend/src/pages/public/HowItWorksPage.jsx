import SeoHelmet from '../../components/SeoHelmet.jsx';
import { useLocale } from '../../context/LocaleContext.jsx';
import { publicContent } from '../../mocks/publicContent.js';

const flow = [
  {
    id: 'brief',
    title: 'Бриф и скоринг',
    description:
      'Уточняем цели, формируем KPI и проверяем проект на риски. Курируем бриф и оцениваем бюджет.',
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
];

const uzFlow = [
  {
    id: 'brief',
    title: 'Brif va skoring',
    description: 'Maqsad va KPI ni aniqlab, loyihani risklarga tekshiramiz.',
  },
  {
    id: 'match',
    title: 'Komanda tanlash',
    description: '48 soat ichida tasdiqlangan mutaxassislar shortlistini beramiz.',
  },
  {
    id: 'kickoff',
    title: 'Start va sprintlar',
    description: 'Escrow byudjetni bosqichlarga bo‘lib, kuratorlar sifatni nazorat qiladi.',
  },
  {
    id: 'review',
    title: 'Qabul va analitika',
    description: 'Feedback yig‘amiz va ROI ni hisoblab, keyingi ishlarni rejalashtiramiz.',
  },
];

export default function HowItWorksPage() {
  const { locale } = useLocale();
  const copy = locale === 'uz' ? uzFlow : flow;
  const seo = publicContent[locale].seo.howItWorks;

  return (
    <div className="card" data-analytics-id="how-it-works">
      <SeoHelmet title={seo.title} description={seo.description} path="/how-it-works" />
      <header className="section-header">
        <div>
          <h1>{seo.title}</h1>
          <p>{seo.description}</p>
        </div>
      </header>
      <div className="grid two">
        {copy.map((step, index) => (
          <article key={step.id} className="step-card">
            <div className="step-index">0{index + 1}</div>
            <h2>{step.title}</h2>
            <p>{step.description}</p>
          </article>
        ))}
      </div>
      <section className="card" style={{ marginTop: '2rem' }}>
        <h2>{locale === 'uz' ? 'Monitoring va eskalatsiya' : 'Мониторинг и эскалации'}</h2>
        <ul>
          <li>
            {locale === 'uz'
              ? 'Kundalik прогресс-репортlar va SLA bo‘yicha avtomatik xabarlar.'
              : 'Ежедневные отчёты о прогрессе и автоматические уведомления по SLA.'}
          </li>
          <li>
            {locale === 'uz'
              ? 'Escrow statusi графанада ko‘rsatiladi, buzilish bo‘lsa — алёрт.'
              : 'Статус escrow отражается в Grafana; при отклонениях срабатывает алёрт.'}
          </li>
          <li>
            {locale === 'uz'
              ? 'KPI bajarilmasa, kuраторlar жалобani 4 soatda ko‘rib chiqadi.'
              : 'При нарушении KPI куратор инициирует разбор в течение 4 часов.'}
          </li>
        </ul>
      </section>
    </div>
  );
}
