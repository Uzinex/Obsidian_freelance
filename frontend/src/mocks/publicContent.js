export const publicContent = {
  ru: {
    seo: {
      home: {
        title: 'Obsidian Freelance — IT-платформа с безопасным escrow',
        description:
          'Соединяем компании и фрилансеров в Узбекистане для запуска digital-проектов с прозрачными условиями и защитой платежей.',
        ogImage: 'https://cdn.obsidianfreelance.com/meta/ru-home.png',
      },
      howItWorks: {
        title: 'Как работает Obsidian Freelance',
        description: 'Пошаговая схема запуска IT-проектов и контроля качества через escrow и кураторов.',
      },
      escrow: {
        title: 'Escrow-сделки и защита платежей',
        description:
          'Финансовые гарантии для заказчиков и исполнителей: заморозка бюджета, staged-платежи и прозрачные логи.',
      },
      categories: {
        title: 'Категории и навыки — витрина команды',
        description: 'Выбирайте экспертов по отрасли, стеку и уровню. Обновление раз в неделю.',
      },
      profile: {
        title: 'Публичный профиль специалиста Obsidian Freelance',
        description: 'Примеры релевантных проектов, стек, отзывы и доступность для заказов.',
      },
      faq: {
        title: 'FAQ — часто задаваемые вопросы',
        description: 'Собрали ответы про escrow, безопасность и запуск проектов.',
      },
      blog: {
        title: 'Блог и новости платформы Obsidian',
        description: 'Обновления продукта, кейсы команд и инсайты по работе в Узбекистане.',
      },
      orders: {
        title: 'Биржа IT-заказов Obsidian Freelance',
        description: 'Актуальные проекты с дедлайнами, бюджетами и escrow-защитой.',
      },
      freelancers: {
        title: 'Каталог проверенных фрилансеров',
        description: 'Команды и специалисты с KYC-верификацией и SLA по ответам.',
      },
      pricing: {
        title: 'Тарифы и комиссии Obsidian Freelance',
        description: 'Escrow, кураторство и выплаты в сумах без скрытых условий.',
      },
      about: {
        title: 'О платформе Obsidian Freelance',
        description: 'Кураторская команда и партнёры, которые строят рынок удалённой работы в Узбекистане.',
      },
      contacts: {
        title: 'Контакты и about-команда',
        description: 'Офисы в Ташкенте и Самарканде, быстрая поддержка 24/7.',
      },
      legal: {
        terms: {
          title: 'Условия использования Obsidian Freelance',
          description: 'Права и обязанности пользователей платформы.',
        },
        privacy: {
          title: 'Политика конфиденциальности',
          description: 'Как мы храним и обрабатываем данные пользователей.',
        },
        cookies: {
          title: 'Политика Cookie',
          description: 'Какие cookie применяются на публичных страницах.',
        },
      },
    },
    organization: {
      name: 'Obsidian Freelance',
      url: 'https://obsidianfreelance.com/ru',
      logo: 'https://cdn.obsidianfreelance.com/meta/logo-dark.svg',
      sameAs: ['https://t.me/obsidianfreelance', 'https://www.linkedin.com/company/obsidianfreelance'],
      aggregateRating: {
        ratingValue: '4.9',
        reviewCount: '124',
      },
    },
    pricing: {
      tiers: [
        {
          name: 'Escrow Base',
          price: 0,
          currency: 'UZS',
          description: 'Базовый тариф для сделок до 100 млн сум.',
          features: ['Freeze бюджета в банке-партнёре', 'Контроль этапов и артефактов', 'Стандартный SLA 8 часов'],
        },
        {
          name: 'Growth+',
          price: 0.025,
          currency: 'budget_share',
          description: 'Куратор и автоматизация платежей для продуктовых команд.',
          features: ['Персональный куратор', 'Гибридные выплаты (UZCARD, Swift)', 'SLA 2 часа на спор'],
        },
        {
          name: 'Enterprise Escrow',
          price: 'custom',
          currency: 'UZS',
          description: 'Мультивалютные сделки и публичный аудит логов.',
          features: ['DPA и audit log', 'Выплаты в UZS/USD', 'Приоритетный саппорт 24/7'],
        },
      ],
      payouts: [
        'Пополнение через Uzcard/Humo, корпоративный счёт или Swift.',
        'Выплаты на карты Uzcard/Humo, юридические лица и SWIFT-компании.',
        'Комиссия за ввод/вывод — 0%, банк удерживает собственные тарифы.',
      ],
      changelog: [
        { version: '2025.01', date: '2025-01-04', summary: 'Добавлен автоматический расчёт staged-платежей.' },
        { version: '2024.12', date: '2024-12-10', summary: 'Расширена отчётность по Escrow в личном кабинете.' },
        { version: '2024.11', date: '2024-11-02', summary: 'Появился публичный лог споров и SLA.' },
      ],
      offers: [
        {
          '@type': 'Offer',
          priceCurrency: 'UZS',
          price: '0',
          description: 'Escrow Base без комиссии за ввод средств.',
          name: 'Escrow Base',
        },
        {
          '@type': 'Offer',
          priceCurrency: 'UZS',
          price: '2.5%',
          description: 'Growth+ с кураторством и автоматизацией.',
          name: 'Growth+ Escrow',
        },
      ],
    },
    reviews: [
      {
        author: 'Камола Юсупова',
        role: 'Product Lead',
        rating: 5,
        review: 'За два спринта собрали команду аналитиков и дизайнеров, escrow снял риски бюджета.',
      },
      {
        author: 'Сардор Эргашев',
        role: 'CTO AgroTech',
        rating: 5,
        review: 'Работаем с платформой для DevOps-поддержки — SLA и платёжная дисциплина без сюрпризов.',
      },
    ],
    faq: [
      {
        question: 'Как работает escrow?',
        answer:
          'Бюджет блокируется на счету партнёрского банка. После приёмки спринта средства автоматически переходят исполнителям.',
      },
      {
        question: 'Сколько стоит подбор команды?',
        answer: 'Комиссия включена в бюджет сделки, отдельной подписки нет.',
      },
      {
        question: 'Можно ли приглашать своих фрилансеров?',
        answer: 'Да, используйте инструмент Invite — вы даёте доступ к трекингу задач и защищённым платежам.',
      },
    ],
    blog: [
      {
        slug: 'escrow-playbook',
        title: 'Escrow playbook: как не терять бюджет на больших задачах',
        description: 'Чек-лист для команд, запускающих digital-проекты с внешними подрядчиками.',
        publishedAt: '2024-12-15',
        readingTime: '6 мин',
        cover: 'https://cdn.obsidianfreelance.com/blog/escrow-playbook.png',
        author: 'Лола Ганиева',
        tags: ['escrow', 'финансы'],
        body: [
          'Сегмент digital-услуг в Узбекистане растёт, но до 38% проектов срывают сроки из-за распылённой ответственности.',
          'Escrow-контур позволяет заморозить бюджет, разбить оплату на этапы и фиксировать артефакты приёмки.',
        ],
      },
      {
        slug: 'observability-launch',
        title: 'Наблюдаемость для маркетинговых страниц',
        description: 'Как мы построили конвейер метрик и алёртов для публичных воронок.',
        publishedAt: '2025-01-04',
        readingTime: '4 мин',
        cover: 'https://cdn.obsidianfreelance.com/blog/observability.png',
        author: 'Дмитрий Асадов',
        tags: ['observability', 'marketing'],
        body: [
          'Команда growth собрала единый слой событий: scroll, CTA, кросс-локальные конверсии.',
          'На Grafana добавлены алёрты по падению CR и росту 404, плюс Sentry для SSG.',
        ],
      },
    ],
    categories: [
      { name: 'Продуктовая аналитика', description: 'Аналитики product & growth', slug: 'product-analytics' },
      { name: 'Machine Learning', description: 'ML-инженеры и MLOps', slug: 'machine-learning' },
      { name: 'UX/UI дизайн', description: 'Исследования, CJM и дизайн-системы', slug: 'ux-ui' },
      { name: 'DevOps', description: 'CI/CD, Kubernetes, безопасность', slug: 'devops' },
    ],
    skills: ['Go', 'Python', 'Next.js', 'Kotlin', 'Figma', 'Terraform', 'PostgreSQL', 'Kafka'],
    profiles: [
      {
        slug: 'sardor-karimov',
        name: 'Сардор Каримов',
        title: 'Senior ML Engineer',
        location: 'Ташкент',
        rate: '$45/час',
        availability: '40 часов / неделя',
        bio: '8 лет в ML, запуск рекомендательных систем и computer vision.',
        skills: ['Python', 'TensorFlow', 'MLOps'],
        portfolio: [
          {
            title: 'Детекция качества хлопка',
            description: 'Модель CV снизила потери сырья на 12%.',
          },
          {
            title: 'Рекомендательная система ритейлера',
            description: 'Повышение LTV на 18% за счёт персонализации.',
          },
        ],
        testimonials: [
          {
            author: 'Dilshod, CTO fintech',
            text: 'Ускорил time-to-market модели скоринга, выстроил ML observability.',
          },
        ],
      },
    ],
  },
  uz: {
    seo: {
      home: {
        title: 'Obsidian Freelance — xavfsiz escrow bilan IT birja',
        description:
          'Kompaniyalar va frilanserlarni raqamli loyihalar uchun bogʻlaymiz: shaffof jarayonlar va kafolatlangan toʻlovlar.',
        ogImage: 'https://cdn.obsidianfreelance.com/meta/uz-home.png',
      },
      howItWorks: {
        title: 'Platforma qanday ishlaydi',
        description: 'Brifdan qabulgacha bo‘lgan yo‘l, kuratorlar va escrow himoyasi.',
      },
      escrow: {
        title: 'Escrow va toʻlovlarni himoyalash',
        description: 'Budjet muzlatiladi va etaplarga boʻlinadi, barcha loglar kuzatuvda.',
      },
      categories: {
        title: 'Kategoriya va skill vitrinasi',
        description: 'Har hafta yangilanadigan malakali mutaxassislar reytingi.',
      },
      profile: {
        title: 'Obsidian mutaxassisi profili',
        description: 'Stack, tajriba va baholar — buyurtmachilar uchun ochiq.',
      },
      faq: {
        title: 'Ko‘p beriladigan savollar',
        description: 'Escrow, xavfsizlik va takliflar haqida javoblar.',
      },
      blog: {
        title: 'Blog va yangiliklar',
        description: 'Mahsulot yangilanishlari hamda muvaffaqiyat hikoyalari.',
      },
      orders: {
        title: 'Obsidian Freelancer — buyurtmalar vitrinasi',
        description: 'Escrow bilan himoyalangan loyihalar va tezkor filtrlar.',
      },
      freelancers: {
        title: 'Tekshirilgan frilanserlar katalogi',
        description: 'KYC va SLA bilan tasdiqlangan jamoalar.',
      },
      pricing: {
        title: 'Tariflar va komissiyalar',
        description: 'Escrow, kuratorlik va to‘lovlar bo‘yicha shaffof jadval.',
      },
      about: {
        title: 'Obsidian haqida',
        description: 'Kuratorlar va hamkorlar bozorda yangi meʼyorlarni yaratadi.',
      },
      contacts: {
        title: 'Kontaktlar',
        description: 'Toshkentdagi ofis va 24/7 qo‘llab-quvvatlash.',
      },
      legal: {
        terms: { title: 'Foydalanish shartlari', description: 'Platformadan foydalanish qoidalari.' },
        privacy: { title: 'Maxfiylik siyosati', description: 'Maʼlumotlarni qayta ishlash tartibi.' },
        cookies: { title: 'Cookie siyosati', description: 'Cookie fayllardan foydalanish.' },
      },
    },
    pricing: {
      tiers: [
        {
          name: 'Escrow Base',
          price: 0,
          currency: 'UZS',
          description: '100 mln so‘mgacha bo‘lgan loyihalar uchun standart paket.',
          features: ['Bank hisobida mablag‘ni muzlatish', 'Bosqichma-bosqich to‘lov', 'SLA 8 soat ichida javob'],
        },
        {
          name: 'Growth+',
          price: 0.025,
          currency: 'budget_share',
          description: 'Kurator va avtomatlashtirilgan to‘lovlar bilan paket.',
          features: ['Shaxsiy kurator', 'Uzcard/Humo va Swift to‘lovlari', 'SLA 2 soat ichida javob'],
        },
        {
          name: 'Enterprise Escrow',
          price: 'custom',
          currency: 'UZS',
          description: 'Katta korporativ loyihalar uchun moslashtirilgan shartlar.',
          features: ['Audit log', 'Valyutalararo to‘lovlar', '24/7 qo‘llab-quvvatlash'],
        },
      ],
      payouts: [
        'Uzcard/Humo, korporativ hisob va Swift orqali mablag‘ kiritish.',
        'To‘lovlar Uzcard/Humo kartalari va yuridik shaxslarga o‘tkazmalar orqali.',
        'Kiritish/chiqarish uchun platforma komissiyasi 0%.',
      ],
      changelog: [
        { version: '2025.01', date: '2025-01-04', summary: 'Staged-to‘lovlar uchun avtomatik hisoblash joriy qilindi.' },
        { version: '2024.12', date: '2024-12-10', summary: 'Escrow holatlari bo‘yicha yangilangan hisobotlar.' },
        { version: '2024.11', date: '2024-11-02', summary: 'Ochiq escrow changelog bo‘limi qo‘shildi.' },
      ],
      offers: [
        {
          '@type': 'Offer',
          priceCurrency: 'UZS',
          price: '0',
          description: 'Escrow Base — kichik loyihalar uchun bepul.',
          name: 'Escrow Base',
        },
        {
          '@type': 'Offer',
          priceCurrency: 'UZS',
          price: '2.5%',
          description: 'Growth+ — kurator va avtomatlashtirish bilan.',
          name: 'Growth+ Escrow',
        },
      ],
    },
    organization: {
      name: 'Obsidian Freelance',
      url: 'https://obsidianfreelance.com/uz',
      logo: 'https://cdn.obsidianfreelance.com/meta/logo-dark.svg',
      sameAs: ['https://t.me/obsidianfreelance', 'https://www.linkedin.com/company/obsidianfreelance'],
      aggregateRating: {
        ratingValue: '4.9',
        reviewCount: '124',
      },
    },
    reviews: [
      {
        author: 'Madina Kamolova',
        role: 'Growth menejeri',
        rating: 5,
        review: 'Kuratorlar yordamida dizayn va development bir sprintda start oldi.',
      },
      {
        author: 'Azizbek Rustamov',
        role: 'COO HealthTech',
        rating: 5,
        review: 'Escrow bizga budjetni nazorat qilish va to‘lovlarni bosqichma-bosqich qilishga yordam berdi.',
      },
    ],
    faq: [
      {
        question: 'Escrow qanday ishlaydi?',
        answer: 'Budjet bank hisobida bloklanadi va qabul qilingach ijrochiga o‘tkaziladi.',
      },
      {
        question: 'Platforma komissiyasi qancha?',
        answer: 'Komissiya bitim byudjetiga kiritilgan, qo‘shimcha to‘lov yo‘q.',
      },
      {
        question: 'O‘z frilanserimni ulashim mumkinmi?',
        answer: 'Ha, Invite vositasi orqali kuzatuv va to‘lovlarni platformaga olib kelasiz.',
      },
    ],
    blog: [
      {
        slug: 'escrow-playbook',
        title: 'Escrow playbook: katta loyihalarda xavfsiz to‘lovlar',
        description: 'Tashqi pudratchilar bilan ishlaydigan komandalar uchun tekshiruv ro‘yxati.',
        publishedAt: '2024-12-15',
        readingTime: '6 daqiqa',
        cover: 'https://cdn.obsidianfreelance.com/blog/escrow-playbook.png',
        author: 'Lola Ganieva',
        tags: ['escrow', 'moliyaviy boshqaruv'],
        body: [
          'Raqamli xizmatlar bozori o‘smoqda, ammo 38% loyihalarda javobgarlik bo‘linishi tufayli kechikishlar kuzatiladi.',
          'Escrow orqali to‘lovlarni bosqichlarga bo‘lib, qabul aktlarini hujjatlashtiramiz.',
        ],
      },
      {
        slug: 'observability-launch',
        title: 'Ommaviy sahifalar uchun kuzatuv tizimi',
        description: 'Vaziyatni real vaqt rejimida ko‘rish va signal berish uchun metrikalar.',
        publishedAt: '2025-01-04',
        readingTime: '4 daqiqa',
        cover: 'https://cdn.obsidianfreelance.com/blog/observability.png',
        author: 'Dmitry Asadov',
        tags: ['observability', 'marketing'],
        body: [
          'Growth jamoasi scroll va CTA eventlarini yagona qatlamga to‘pladi.',
          'Grafana orqali konversiya pasayishi va 404 ko‘payishiga alertlar qo‘shildi.',
        ],
      },
    ],
    categories: [
      { name: 'Mahsulot analitikasi', description: 'Product va growth analitiklari', slug: 'product-analytics' },
      { name: 'Sunʼiy intellekt', description: 'ML muhandislari va MLOps', slug: 'machine-learning' },
      { name: 'UX/UI dizayn', description: 'Izlanishlar va dizayn tizimlari', slug: 'ux-ui' },
      { name: 'DevOps', description: 'CI/CD va xavfsizlik', slug: 'devops' },
    ],
    skills: ['Go', 'Python', 'Next.js', 'Kotlin', 'Figma', 'Terraform', 'PostgreSQL', 'Kafka'],
    profiles: [
      {
        slug: 'sardor-karimov',
        name: 'Sardor Karimov',
        title: 'Senior ML Engineer',
        location: 'Toshkent',
        rate: '$45/soat',
        availability: '40 soat / hafta',
        bio: '8 yillik tajriba, recommender va CV loyihalari.',
        skills: ['Python', 'TensorFlow', 'MLOps'],
        portfolio: [
          { title: 'Paxta sifati deteksiyasi', description: 'CV modeli yo‘qotishlarni 12% ga kamaytirdi.' },
          { title: 'Retail tavsiya tizimi', description: 'Shaxsiylashtirish orqali LTV +18%.' },
        ],
        testimonials: [
          {
            author: 'Dilshod, fintech CTO',
            text: 'Skoring modelini tezlashtirdi va ML observability joriy qildi.',
          },
        ],
      },
    ],
  },
};

export function findArticleBySlug(locale, slug) {
  const list = publicContent[locale]?.blog ?? [];
  return list.find((article) => article.slug === slug);
}
