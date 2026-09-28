export const formatCurrency = (amount: number | null | undefined): string => {
  if (amount === null || amount === undefined) {
    return 'Not publicly observed';
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatCurrencyShort = (amount: number | null | undefined): string => {
  if (amount === null || amount === undefined) {
    return 'N/A';
  }
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  }
  if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} L`;
  }
  if (amount >= 1000) {
    return `₹${(amount / 1000).toFixed(1)} k`;
  }
  return `₹${amount.toLocaleString('en-IN')}`;
};

export const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) {
    return 'Not publicly observed';
  }
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return 'Not publicly observed';
    return d.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return 'Not publicly observed';
  }
};

export const formatDateTime = (dateString: string | null | undefined): string => {
  if (!dateString) {
    return 'Not publicly observed';
  }
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return 'Not publicly observed';
    return d.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return 'Not publicly observed';
  }
};

export const formatText = (value: string | null | undefined, fallback = 'Not publicly observed'): string => {
  if (value === null || value === undefined || value.trim() === '') {
    return fallback;
  }
  return value;
};
