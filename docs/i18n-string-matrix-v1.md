# i18n string matrix v1

## Content inventory
| Domain | Description | Examples |
| --- | --- | --- |
| app_ui | Application chrome, forms, validation copy, empty states, in-product education, system errors. | Header nav, login screen, profile wallet, dispute backoffice, chat. |
| emails | Transactional and lifecycle email templates (registration, verification, 2FA, escrow, disputes, reviews, payouts). | "Verify your account", "Escrow release notice". |
| notifications | In-app feed, push payloads, notification preferences UI. | Notification center filter labels, digest summaries. |
| marketing | Static pages (How it works, Escrow, FAQ, Terms, Privacy, About, Blog, landing sections). | Home hero, About timeline, FAQ accordions. |

## Resource structure
```
frontend/
└─ src/
   └─ locales/
      ├─ app_ui.source.json
      ├─ app_ui.ru.json
      └─ app_ui.uz.json
```
Each locale file mirrors the same flat key space. Example excerpt:
```json
{
  "app_ui.header.nav.home": "Home",
  "app_ui.header.nav.about": "About",
  "app_ui.auth.login.error": "Incorrect login or password.",
  "emails.verification.subject": "Confirm your Obsidian account"
}
```

## Matrix
| Domain | Key | Source (English) | Uz | Ru | Status |
| --- | --- | --- | --- | --- | --- |
| app_ui | app_ui.header.nav.home | Home | Bosh sahifa | Главная | approved |
| app_ui | app_ui.header.nav.orders | Orders | Buyurtmalar | Работы | approved |
| app_ui | app_ui.home.hero.title | Uniting elite teams for ambitious projects | Ambitsiyali loyihalar uchun eng yaxshi jamoalarni birlashtiramiz | Объединяем лучшие команды для амбициозных проектов | in_review |
| app_ui | app_ui.home.hero.secondaryCta | Browse work | Ishlarni ko'rish | Смотреть работы | approved |
| app_ui | app_ui.orders.page.description | Filter live projects by categories, skills, and engagement rules. | Faol loyihalarni yo'nalish, ko'nikma va hamkorlik formati bo'yicha filtrlang. | Фильтруйте открытые проекты по категориям, навыкам и формату сотрудничества. | in_review |
| app_ui | app_ui.orders.list.empty | No matching orders yet. Try adjusting the filters. | Mos buyurtmalar topilmadi. Filtrlarni o'zgartirib ko'ring. | Не найдено подходящих заказов. Попробуйте изменить фильтры. | in_review |
| app_ui | app_ui.auth.login.error | Incorrect login or password. | Login yoki parol noto'g'ri. | Неверный логин или пароль. | approved |
| app_ui | app_ui.auth.register.submit | Sign up | Ro'yxatdan o'tish | Зарегистрироваться | in_review |
| app_ui | app_ui.profile.wallet.empty | Wallet transactions will appear here after your first payout. | Birinchi to'lovdan so'ng operatsiyalar shu yerda ko'rinadi. | Операции появятся здесь после первой выплаты. | new |
| app_ui | app_ui.notificationCenter.filters.category | Category | Kategoriya | Категория | new |
| notifications | notifications.digest.summary | {count} unread notifications in your Obsidian account. | Obsidian akkauntingizda {count} ta o'qilmagan bildirishnoma bor. | В вашем аккаунте Obsidian {count} непрочитанных уведомлений. | in_review |
| notifications | notifications.alert.dispute_opened | Dispute #{case_id} is awaiting your response. | #{case_id} mojarosi sizning javobingizni kutmoqda. | Спор №{case_id} ожидает вашего ответа. | in_review |
| emails | emails.verification.subject | Confirm your Obsidian account | Obsidian akkauntingizni tasdiqlang | Подтвердите аккаунт Obsidian | approved |
| emails | emails.verification.body | Finish verification to unlock contracts and payouts. | Shartnomalar va to'lovlar uchun verifikatsiyani yakunlang. | Завершите верификацию, чтобы открыть контракты и выплаты. | in_review |
| emails | emails.payout.subject | Payout sent for contract #{contract_id} | #{contract_id} shartnomasi uchun to'lov yuborildi | Отправлена выплата по контракту №{contract_id} | new |
| marketing | marketing.home.hero.tagline | Platform for complex digital work | Murakkab raqamli vazifalar uchun platforma | Платформа для сложных цифровых задач | approved |
| marketing | marketing.about.timeline.2024 | Scaled enterprise delivery across EMEA and MENA. | EMEA va MENA bo'ylab korporativ yetkazib berishni kengaytirdik. | Масштабировали корпоративные проекты по EMEA и MENA. | in_review |
| marketing | marketing.escrow.faq.release | When are escrow funds released? | Escrow mablag'lari qachon yechiladi? | Когда выпускаются средства из эскроу? | new |
| marketing | marketing.blog.cta | See all insights | Barcha maqolalarni ko'rish | Смотреть все статьи | in_review |
| notifications | notifications.settings.quietHours | Quiet hours | Tinch soatlar | Тихие часы | approved |
| app_ui | app_ui.chat.quickActions.open_dispute | Open a dispute | Mojaro ochish | Открыть спор | new |

Statuses: `new` = string captured but not yet in TMS, `in_review` = waiting for linguist review, `approved` = fully signed off.
