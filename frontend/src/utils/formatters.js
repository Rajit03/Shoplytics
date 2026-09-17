/**
 * Utility formatters for Brazilian Real currency, numbers, dates, and percentages.
 */

// Format monetary amounts in Brazilian Real (R$)
export const formatCurrency = (val) => {
  if (val === null || val === undefined || isNaN(val)) return 'R$ 0,00';
  const num = Number(val);
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
};

// Compact number formatting (e.g. 1.5M, 95.4k)
export const formatCompactNumber = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0';
  const num = Number(val);
  return new Intl.NumberFormat('pt-BR', {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  }).format(num);
};

// Standard number formatting with thousands separator
export const formatNumber = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '0';
  const num = Number(val);
  return new Intl.NumberFormat('pt-BR').format(num);
};

// Format percentages
export const formatPercent = (val, decimals = 1) => {
  if (val === null || val === undefined || isNaN(val)) return '0%';
  const num = Number(val);
  return `${num.toFixed(decimals)}%`;
};

// Format date strings
export const formatDate = (val) => {
  if (!val) return '—';
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return new Intl.DateTimeFormat('en-GB', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(d);
  } catch {
    return String(val);
  }
};

// Format date and time
export const formatDateTime = (val) => {
  if (!val) return '—';
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return String(val);
    return new Intl.DateTimeFormat('en-GB', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return String(val);
  }
};
