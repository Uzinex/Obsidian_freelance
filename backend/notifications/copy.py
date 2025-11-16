from __future__ import annotations

from typing import Any

from .formatting import FALLBACK_LOCALES, normalize_locale

DEFAULT_LIST_UNSUBSCRIBE = '<mailto:unsubscribe@obsidian.uz>, <https://obsidian.uz/unsubscribe>'
DEFAULT_LIST_ID = 'notifications.obsidian.uz'

EMAIL_TEMPLATE_ALIASES = {
    'contract.created': 'escrow.opened',
    'contract.signed': 'escrow.hold',
    'contract.dispute_opened': 'dispute.opened',
    'payments.payout': 'payouts.sent',
    'payments.hold': 'escrow.hold',
    'payments.release': 'escrow.release',
}

WEBPUSH_TEMPLATE_ALIASES = EMAIL_TEMPLATE_ALIASES

EMAIL_COPY: dict[str, dict[str, Any]] = {
    'account.registration': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Добро пожаловать в Obsidian',
            'body': 'Привет, {full_name}! Подтвердите аккаунт по ссылке {verification_url}. Срок действия — {token_ttl}.',
        },
        'uz': {
            'subject': 'Obsidian ga xush kelibsiz',
            'body': "Salom, {full_name}! {verification_url} havolasini tasdiqlang. Amal qilish muddati — {token_ttl}.",
        },
    },
    'account.verification': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Верификация профиля запущена',
            'body': 'Мы получили документы и проверим их в течение 48 часов. Статус доступен в профиле.',
        },
        'uz': {
            'subject': 'Profilingiz tekshiruvda',
            'body': 'Hujjatlaringiz qabul qilindi. Tekshiruv 48 soatgacha davom etadi.',
        },
    },
    'account.2fa': {
        'meta': {'category': 'security'},
        'ru': {
            'subject': 'Код двухфакторной аутентификации',
            'body': 'Ваш одноразовый код: {otp}. Он истечёт через {otp_ttl}.',
        },
        'uz': {
            'subject': 'Ikki faktorli kod',
            'body': 'Bir martalik kod: {otp}. Amal qilish muddati — {otp_ttl}.',
        },
    },
    'escrow.opened': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Escrow открыт для контракта №{contract_id}',
            'body': 'Резерв {amount_formatted} создан. Подпишите контракт до {deadline_formatted}.',
        },
        'uz': {
            'subject': '№{contract_id} bo\'yicha escrow ochildi',
            'body': '{amount_formatted} rezervga qo\'yildi. Shartnomani {deadline_formatted} gacha imzolang.',
        },
    },
    'escrow.hold': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Оплата на холде',
            'body': 'Выплата {amount_formatted} заблокирована до подтверждения сдачи работы.',
        },
        'uz': {
            'subject': 'To\'lov holda',
            'body': '{amount_formatted} topshiruv tasdiqlanguncha bloklanadi.',
        },
    },
    'escrow.release': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Выплата отправлена исполнителю',
            'body': 'Клиент подтвердил работу. {amount_formatted} направлены на кошелёк.',
        },
        'uz': {
            'subject': 'To\'lov ijrochiga yuborildi',
            'body': 'Buyurtmachi ishni tasdiqladi. {amount_formatted} hamyonga yo\'l oldi.',
        },
    },
    'escrow.refund': {
        'meta': {'category': 'transactional'},
        'ru': {
            'subject': 'Средства возвращены заказчику',
            'body': 'Escrow по контракту №{contract_id} закрыт. {amount_formatted} вернулись на счёт.',
        },
        'uz': {
            'subject': 'Mablag\' buyurtmachiga qaytarildi',
            'body': '№{contract_id} escrow yopildi. {amount_formatted} hisobingizga qaytdi.',
        },
    },
    'dispute.opened': {
        'meta': {'category': 'compliance'},
        'ru': {
            'subject': 'Открыт спор №{case_id}',
            'body': 'Мы уведомили вторую сторону. Ответ оставьте до {deadline_formatted}.',
        },
        'uz': {
            'subject': '№{case_id} nizo ochildi',
            'body': "Ikkinchi tomon ogohlantirildi. {deadline_formatted} gacha javob bering.",
        },
    },
    'reviews.received': {
        'meta': {'category': 'engagement'},
        'ru': {
            'subject': 'У вас новый отзыв',
            'body': '{author_name} оставил отзыв по контракту №{contract_id}: “{excerpt}”. Ответьте из профиля.',
        },
        'uz': {
            'subject': 'Sizga yangi fikr qoldirildi',
            'body': '{author_name} №{contract_id} bo\'yicha “{excerpt}” yozdi.',
        },
    },
    'payouts.sent': {
        'meta': {'category': 'finance'},
        'ru': {
            'subject': 'Выплата отправлена',
            'body': '{amount_formatted} перечислены на {payout_method}. Ожидайте поступления до {payout_eta_formatted}.',
        },
        'uz': {
            'subject': 'To\'lov jo\'natildi',
            'body': '{amount_formatted} {payout_method} ga yo\'naltirildi. {payout_eta_formatted} gacha tushadi.',
        },
    },
    'account.login': {
        'meta': {'category': 'security'},
        'ru': {
            'subject': 'Новый вход в аккаунт',
            'body': 'В ваш аккаунт выполнен вход из {location}. Если это не вы — смените пароль.',
        },
        'uz': {
            'subject': 'Hisobga yangi kirish',
            'body': '{location} joyidan tizimga kirildi. Agar bu siz bo\'lmasangiz, parolni almashtiring.',
        },
    },
}

WEBPUSH_COPY: dict[str, dict[str, Any]] = {
    'account.registration': {
        'ru': {'title': 'Аккаунт почти готов', 'body': 'Подтвердите e-mail и опубликуйте первый заказ.'},
        'uz': {'title': 'Profilingiz tayyor bo\'lmoqda', 'body': 'E-mail ni tasdiqlang va buyurtma yarating.'},
    },
    'account.verification': {
        'ru': {'title': 'Документы приняты', 'body': 'Проверяем данные, уведомим о результате.'},
        'uz': {'title': 'Hujjatlar qabul qilindi', 'body': 'Natijani tez orada xabar qilamiz.'},
    },
    'account.2fa': {
        'ru': {'title': 'Подтвердите вход', 'body': 'Введите код 2FA, чтобы завершить авторизацию.'},
        'uz': {'title': 'Kirishni tasdiqlang', 'body': 'Avtorizatsiyani yakunlash uchun 2FA kodini kiriting.'},
    },
    'escrow.opened': {
        'ru': {'title': 'Escrow активен', 'body': 'Резерв на {amount_formatted} готов. Подпишите контракт.'},
        'uz': {'title': 'Escrow ishga tushdi', 'body': '{amount_formatted} rezervlandi. Shartnomani imzolang.'},
    },
    'escrow.hold': {
        'ru': {'title': 'Оплата на холде', 'body': 'Деньги останутся в escrow до приёмки.'},
        'uz': {'title': 'To\'lov holda', 'body': 'Mablag\' tasdiqlanguncha escrow da qoladi.'},
    },
    'escrow.release': {
        'ru': {'title': 'Выплата отправлена', 'body': '{amount_formatted} уже в пути.'},
        'uz': {'title': 'To\'lov yuborildi', 'body': '{amount_formatted} yo\'lda.'},
    },
    'escrow.refund': {
        'ru': {'title': 'Возврат проведён', 'body': '{amount_formatted} возвращены заказчику.'},
        'uz': {'title': 'Qaytarish bajarildi', 'body': '{amount_formatted} buyurtmachiga qaytdi.'},
    },
    'dispute.opened': {
        'ru': {'title': 'Спор открыт', 'body': 'Ответьте до {deadline_relative}.'},
        'uz': {'title': 'Nizo ochildi', 'body': '{deadline_relative} gacha javob bering.'},
    },
    'reviews.received': {
        'ru': {'title': 'Новый отзыв', 'body': '{author_name} поделился впечатлением.'},
        'uz': {'title': 'Yangi baho', 'body': '{author_name} fikr bildirdi.'},
    },
    'payouts.sent': {
        'ru': {'title': 'Выплата на пути', 'body': '{amount_formatted} скоро поступят.'},
        'uz': {'title': 'To\'lov yo\'lda', 'body': '{amount_formatted} tez orada tushadi.'},
    },
}


def _resolve_key(key: str, aliases: dict[str, str]) -> str:
    return aliases.get(key, key)


def _pick_locale(entry: dict[str, Any], locale: str | None) -> dict[str, Any] | None:
    normalized = normalize_locale(locale)
    for candidate in (normalized, *FALLBACK_LOCALES):
        template = entry.get(candidate)
        if template:
            return template
    for value in entry.values():
        if isinstance(value, dict) and 'subject' in value:
            return value
    return None


def get_email_template(event_type: str, locale: str | None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    key = _resolve_key(event_type, EMAIL_TEMPLATE_ALIASES)
    entry = EMAIL_COPY.get(key)
    if not entry:
        return None, {}
    template = _pick_locale({k: v for k, v in entry.items() if k != 'meta'}, locale)
    return template, entry.get('meta', {})


def get_webpush_template(event_type: str, locale: str | None) -> dict[str, Any] | None:
    key = _resolve_key(event_type, WEBPUSH_TEMPLATE_ALIASES)
    entry = WEBPUSH_COPY.get(key)
    if not entry:
        return None
    return _pick_locale(entry, locale)
