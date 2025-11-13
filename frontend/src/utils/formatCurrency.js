const formatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'UZS',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function formatCurrency(amount, currency = 'UZS') {
  if (amount === null || amount === undefined) {
    return '';
  }
  const numeric = Number(amount);
  if (Number.isNaN(numeric)) {
    return `${amount} ${currency}`;
  }
  if (currency !== 'UZS') {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
    }).format(numeric);
  }
  return formatter.format(numeric);
}
