# AI UX Copy Library (UZ/RU)

## Дисклеймеры / Disclaimers
| Context | RU | UZ |
| --- | --- | --- |
| Общий | «AI-коуч предлагает идеи, но решение остаётся за вами. Это не юридическая и не финансовая консультация.» | «AI-kouch gʻoyalar beradi, yakuniy qaror faqat sizniki. Bu huquqiy yoki moliyaviy maslahat emas.» |
| Escrow | «Проводите оплату только через escrow — так мы защищаем обе стороны.» | «Toʻlovni faqat escrow orqali qiling — shu tariqa biz ikki tomonni ham himoya qilamiz.» |
| Privacy | «Не делитесь контактами и приватными данными в подсказках.» | «Promptlarda kontakt va shaxsiy maʼlumotlarni yozmang.» |

## Подсказки «Как использовать коуч»
| Variant | RU | UZ |
| --- | --- | --- |
| Короткий | «Опишите задачу и цели — коуч предложит план действий.» | «Vazifa va maqsadni yozing — kouch harakat rejasini taklif qiladi.» |
| Длинный | «Расскажите, что хотите улучшить (скиллы, профиль, проект). Чем конкретнее запрос, тем точнее подсказки и примеры.» | «Qaysi narsani yaxshilamoqchisiz (koʻnikma, profil, loyiha) deb yozing. Soʻrov qancha aniq boʻlsa, tavsiyalar shuncha foydali boʻladi.» |

## Статусы генерации
| State | RU | UZ |
| --- | --- | --- |
| Старт / Idle | «Готовы к новым идеям» | «Yangi gʻoyalar uchun tayyorman» |
| Генерируем (stream) | «Генерируем подсказку…» | «Prompt yaratilmoqda…» |
| Ошибка | «Что-то пошло не так. Попробуйте ещё раз или сообщите о проблеме.» | «Nimadir xato ketdi. Yana urinib koʻring yoki xabar bering.» |
| Повторить | «Повторить генерацию» | «Qayta yaratish» |

## Элементы статуса и действий в UI
- **Индикатор стриминга**: анимированная строка «AI печатает… / AI yozmoqda…».
- **Кнопки**: «Копировать всё», «Вставить в чат», «Пожаловаться», «Отключить AI». Все строки локализованы.
- **Пустые состояния**: карточка с иконкой лампы, текст «Поделитесь задачей — AI предложит идеи» (RU) / «Vazifani yozing — AI gʻoyalarni beradi» (UZ).
- **Маленькие обучающие блоки**: чек-лист «Сформулируйте цель → Уточните ограничения → Выберите действие» / «Maqsad → Cheklovlar → Harakat».

## Варианты подсказок
| Audience | Variant | RU | UZ |
| --- | --- | --- | --- |
| Фрилансер | Короткий | «Опишите проект, сроки и уровень клиента — коуч предложит, как повысить шанс матчинга.» | «Loyiha, muddat va mijoz turini yozing — kouch moslik imkonini oshirishni aytadi.» |
| Фрилансер | Длинный | «Расскажите, какие отклики уже пробовали, что сработало и где нужен совет. Коуч подсветит сильные стороны и доработает текст отклика.» | «Qanday javoblar berganingizni, nima ishlaganini va qayerda maslahat kerakligini yozing. Kouch kuchli tomonlarni ko‘rsatib, javob matnini yaxshilaydi.» |
| Клиент | Короткий | «Опишите требуемые навыки и бюджет — AI предложит, как сформировать задачу.» | «Kerakli koʻnikmalar va budjetni yozing — AI vazifani qanday tuzishni aytadi.» |
| Клиент | Длинный | «Укажите контекст проекта, критерии успеха и процессы проверки. Коуч поможет собрать бриф и check-list для escrow.» | «Loyiha konteksti, muvaffaqiyat mezonlari va tekshiruv jarayonlarini yozing. Kouch brif va escrow uchun check-list tuzishga yordam beradi.» |

## Совместимость с i18n
- Любая строка хранится в `ai.copyLibrary[locale]` и проходит через локализацию.
- Текст автоматически переносится, чтобы не ломать сетку; для длинных подсказок используем max-width и clamp.
