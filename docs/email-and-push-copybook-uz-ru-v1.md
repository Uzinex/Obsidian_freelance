# Email & Push Copybook (uz/ru)

## Матрица событий и fallback
- Ключи шаблонов совпадают с внутренними event_type:
  - `account.registration`
  - `account.verification`
  - `account.2fa`
  - `escrow.opened`
  - `escrow.hold`
  - `escrow.release`
  - `escrow.refund`
  - `dispute.opened`
  - `reviews.received`
  - `payouts.sent`
- Локали: `ru`, `uz`. Если язык пользователя неизвестен — используем `ru`, затем `uz` как запасной вариант (см. `backend/notifications/copy.py`).
- Письма содержат локализованные темы и `List-*` заголовки:
  - `List-Unsubscribe: <mailto:unsubscribe@obsidian.uz>, <https://obsidian.uz/unsubscribe>`
  - `List-Unsubscribe-Post: List-Unsubscribe=One-Click`
  - `List-ID: notifications.obsidian.uz`
  - `Precedence: list` (или `bulk` для дайджестов)

## Регистрация (`account.registration`)
| Канал | Локаль | Тема / Title | Текст |
|-------|--------|--------------|-------|
| Email | ru | Добро пожаловать в Obsidian | Привет, {full_name}! Чтобы опубликовать заказ и получать офферы, подтвердите почту по ссылке {verification_url}. Срок действия — {token_ttl}.
| Email | uz | Obsidian ga xush kelibsiz | Salom, {full_name}! Buyurtma joylash va takliflarni olish uchun {verification_url} havolasini tasdiqlang. Havola {token_ttl} ichida amal qiladi.
| Push | ru | Аккаунт почти готов | Завершите регистрацию и получите доступ к маркетплейсу.
| Push | uz | Profilingiz deyarli tayyor | Ro'yxatdan o'tishni yakunlang va buyurtmalarni ko'ring.

## Верификация (`account.verification`)
| Канал | Локаль | Тема / Title | Текст |
|-------|--------|--------------|-------|
| Email | ru | Верификация профиля запущена | Мы получили документы. Проверка займёт до 48 часов. Статус отслеживается в профиле.
| Email | uz | Profilingiz tekshiruvda | Hujjatlaringizni oldik. Tekshiruv 48 soatgacha davom etadi. Holatni profil orqali kuzating.
| Push | ru | Документы приняты | Проверяем данные и уведомим о результате.
| Push | uz | Hujjatlar qabul qilindi | Natijani xabar qilamiz.

## 2FA (`account.2fa`)
| Канал | Локаль | Тема / Title | Текст |
|-------|--------|--------------|-------|
| Email | ru | Код двухфакторной аутентификации | Ваш одноразовый код: {otp}. Он истечёт через {otp_ttl}.
| Email | uz | Ikki faktorli kod | Bir martalik kodingiz: {otp}. Amal qilish muddati — {otp_ttl}.
| Push | ru | Подтвердите вход | Используйте код 2FA, чтобы завершить авторизацию.
| Push | uz | Kirishni tasdiqlang | Avtorizatsiyani yakunlash uchun 2FA kodidan foydalaning.

## Escrow (`escrow.opened`, `escrow.hold`, `escrow.release`, `escrow.refund`)
| Событие | Локаль | Email тема | Email тело | Push title / body |
|---------|--------|------------|------------|-------------------|
| opened | ru | Escrow открыт для контракта №{contract_id} | Средства {amount_formatted} зарезервированы на счёте. Подпишите контракт до {deadline_formatted}. | Escrow активен — подпишите контракт. / Резерв на {amount_formatted} готов.
| opened | uz | №{contract_id} bo'yicha escrow ochildi | {amount_formatted} mablag' rezervga qo'yildi. Shartnomani {deadline_formatted} gacha imzolang. | Escrow faollashtirildi. / Rezerv tayyor, shartnomani imzolang.
| hold | ru | Оплата на холде | Выплата {amount_formatted} заблокирована до подтверждения сдачи работы. | Деньги зарезервированы до приёмки.
| hold | uz | To'lov holda | {amount_formatted} topshiruv tasdiqlanguncha bloklanadi. | Mablag' tasdiqlanguncha bloklangan.
| release | ru | Выплата отправлена исполнителю | Клиент подтвердил работу. {amount_formatted} направлены на кошелёк. | Выплата {amount_formatted} отправлена.
| release | uz | To'lov ijrochiga yuborildi | Buyurtmachi ishni tasdiqladi. {amount_formatted} hamyoningizga yo'l oldi. | {amount_formatted} to'lovi yuborildi.
| refund | ru | Средства возвращены заказчику | Escrow по контракту №{contract_id} разблокирован. {amount_formatted} вернулись на счёт. | Возврат {amount_formatted} проведён.
| refund | uz | Mablag' buyurtmachiga qaytarildi | №{contract_id} escrow bekor qilindi. {amount_formatted} hisobingizga qaytdi. | Qaytarish {amount_formatted} amalga oshdi.

## Споры (`dispute.opened`)
| Канал | Локаль | Тема / Title | Текст |
| Email | ru | Открыт спор №{case_id} | Мы уведомили вторую сторону. Ответ нужно оставить до {deadline_formatted}. | Push: Спор открыт → Ответьте до {deadline_relative}.
| Email | uz | №{case_id} nizo ochildi | Ikkinchi tomon ogohlantirildi. {deadline_formatted} gacha javob qoldiring. | Push: Nizo ochildi → {deadline_relative} gacha javob bering.

## Отзывы (`reviews.received`)
| Канал | Локаль | Тема / Title | Текст |
| Email | ru | У вас новый отзыв | {author_name} оставил отзыв по контракту №{contract_id}: “{excerpt}”. Ответьте из профиля. |
| Email | uz | Sizga yangi fikr qoldirildi | {author_name} №{contract_id} bo'yicha “{excerpt}” yozdi. Profil orqali javob qaytaring. |
| Push | ru | Новый отзыв | {author_name} поделился впечатлением.
| Push | uz | Yangi baho | {author_name} tajriba bilan o'rtoqlashdi.

## Пейауты (`payouts.sent`)
| Канал | Локаль | Тема / Title | Текст |
| Email | ru | Выплата отправлена | {amount_formatted} перечислены на {payout_method}. Ожидаем зачисления до {payout_eta}. |
| Email | uz | To'lov jo'natildi | {amount_formatted} {payout_method} ga yo'naltirildi. Mablag' {payout_eta} gacha tushadi. |
| Push | ru | Выплата на пути | Следите за статусом в кошельке.
| Push | uz | To'lov yo'lda | Hamyoningizda holatni tekshiring.

## Дополнительно
- Все шаблоны доступны в `backend/notifications/copy.py` и синхронизированы с UI текстами (`frontend/src/locales/...`).
- Для дайджестов/уведомлений действуют заголовки `List-ID`/`Precedence`, описанные выше. `List-Unsubscribe` добавляется даже для триггерных писем, чтобы снизить жалобы.
- Push-тексты ограничены 90 символами. Плейсхолдеры `{amount_formatted}`, `{deadline_relative}` формируются хелперами.
