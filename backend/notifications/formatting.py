from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping
from zoneinfo import ZoneInfo

SUPPORTED_LOCALES = ('ru', 'uz')
FALLBACK_LOCALES = ('ru', 'uz')
TASHKENT_TZ = ZoneInfo('Asia/Tashkent')

THOUSANDS_SEPARATOR = {
  'ru': '\xa0',
  'uz': '\xa0',
}

DECIMAL_SEPARATOR = {
  'ru': ',',
  'uz': '.',
}

CURRENCY_LABELS = {
  'ru': {'UZS': 'сум'},
  'uz': {'UZS': "so'm"},
}

PLURAL_RULES = {
  'ru': ('one', 'few', 'many', 'other'),
  'uz': ('one', 'other'),
}


def normalize_locale(locale: str | None) -> str:
  normalized = (locale or '').lower().split('_')[0].split('-')[0]
  if normalized in SUPPORTED_LOCALES:
    return normalized
  return FALLBACK_LOCALES[0]


def _to_decimal(value: Any) -> Decimal:
  if isinstance(value, Decimal):
    return value
  try:
    return Decimal(str(value))
  except (InvalidOperation, ValueError, TypeError):
    raise InvalidOperation from None


def format_number(value: Any, *, locale: str | None = None, fraction_digits: int = 0) -> str:
  normalized = normalize_locale(locale)
  try:
    decimal_value = _to_decimal(value)
  except InvalidOperation:
    return str(value)
  quantize_exp = Decimal('1') if fraction_digits <= 0 else Decimal(10) ** -fraction_digits
  quantized = decimal_value.quantize(quantize_exp)
  sign = '-' if quantized < 0 else ''
  int_part, _, frac_part = f"{abs(quantized):f}".partition('.')
  groups = []
  while int_part:
    groups.insert(0, int_part[-3:])
    int_part = int_part[:-3]
  separator = THOUSANDS_SEPARATOR.get(normalized, '\xa0')
  decimal_sep = DECIMAL_SEPARATOR.get(normalized, '.')
  formatted = separator.join(groups) or '0'
  if fraction_digits > 0:
    frac = (frac_part + '0' * fraction_digits)[:fraction_digits]
    formatted = f"{formatted}{decimal_sep}{frac}"
  return f"{sign}{formatted}"


def format_currency(amount: Any, *, currency: str = 'UZS', locale: str | None = None) -> str:
  normalized = normalize_locale(locale)
  digits = 0 if currency == 'UZS' else 2
  number = format_number(amount, locale=normalized, fraction_digits=digits)
  suffix = CURRENCY_LABELS.get(normalized, {}).get(currency, currency)
  return f"{number} {suffix}".strip()


def format_datetime(value: Any, *, locale: str | None = None, pattern: str = '%d.%m.%Y %H:%M') -> str:
  locale = normalize_locale(locale)
  if value is None:
    return ''
  if isinstance(value, str):
    try:
      parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
      return value
  elif isinstance(value, datetime):
    parsed = value
  else:
    return str(value)
  localized = parsed.astimezone(TASHKENT_TZ)
  return localized.strftime(pattern)


def format_date(value: Any, *, locale: str | None = None) -> str:
  return format_datetime(value, locale=locale, pattern='%d.%m.%Y')


def format_relative_date(value: Any, *, locale: str | None = None, threshold_days: int = 7) -> str:
  locale = normalize_locale(locale)
  if value is None:
    return ''
  if isinstance(value, str):
    try:
      parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
      return value
  elif isinstance(value, datetime):
    parsed = value
  else:
    return str(value)
  target = parsed.astimezone(TASHKENT_TZ).date()
  today = datetime.now(tz=TASHKENT_TZ).date()
  delta = (target - today).days
  if delta == 0:
    return 'сегодня' if locale == 'ru' else 'bugun'
  if delta == -1:
    return 'вчера' if locale == 'ru' else 'kecha'
  if delta == 1:
    return 'завтра' if locale == 'ru' else 'ertaga'
  if abs(delta) > threshold_days:
    return format_date(parsed, locale=locale)
  if locale == 'ru':
    unit = format_plural(abs(delta), locale=locale, forms={'one': 'день', 'few': 'дня', 'many': 'дней'})
    template = 'через {count} {unit}' if delta > 0 else '{count} {unit} назад'
  else:
    unit = format_plural(abs(delta), locale=locale, forms={'one': 'kun', 'other': 'kun'})
    template = "yana {count} {unit} ichida" if delta > 0 else '{count} {unit} oldin'
  return template.format(count=abs(delta), unit=unit)


def format_plural(count: int, *, locale: str | None = None, forms: Mapping[str, str] | None = None) -> str:
  locale = normalize_locale(locale)
  forms = forms or {}
  if locale == 'ru':
    mod10 = count % 10
    mod100 = count % 100
    if mod10 == 1 and mod100 != 11:
      category = 'one'
    elif 2 <= mod10 <= 4 and not 12 <= mod100 <= 14:
      category = 'few'
    elif mod10 == 0 or 5 <= mod10 <= 9 or 11 <= mod100 <= 14:
      category = 'many'
    else:
      category = 'other'
  else:
    category = 'one' if count == 1 else 'other'
  return forms.get(category) or forms.get('other') or forms.get('one') or ''


def enrich_context(data: Mapping[str, Any], *, locale: str | None = None) -> dict[str, Any]:
  locale = normalize_locale(locale)
  context = dict(data or {})
  currency = context.get('currency', 'UZS')
  amount_source = context.get('amount') or context.get('budget')
  if amount_source is not None and 'amount_formatted' not in context:
    context['amount_formatted'] = format_currency(amount_source, currency=currency, locale=locale)
  deadline = context.get('deadline') or context.get('due_at')
  if deadline and 'deadline_formatted' not in context:
    context['deadline_formatted'] = format_datetime(deadline, locale=locale)
    context['deadline_relative'] = format_relative_date(deadline, locale=locale)
  if context.get('payout_eta') and 'payout_eta_formatted' not in context:
    context['payout_eta_formatted'] = format_relative_date(context['payout_eta'], locale=locale)
  return context
