// O'zbekcha formatlash yordamchilari — narx, masofa, sana, holat.

export function soum(value) {
  if (value === null || value === undefined || value === '') return '—';
  const n = Number(value);
  if (Number.isNaN(n)) return '—';
  return n.toLocaleString('ru-RU').replace(/ /g, ' ') + " so'm";
}

export function priceRange(from, to) {
  if (from && to && Number(to) > Number(from)) return `${soum(from)} – ${soum(to)}`;
  return soum(from);
}

export function km(value) {
  if (value === null || value === undefined) return null;
  const n = Number(value);
  if (n < 1) return `${Math.round(n * 1000)} m`;
  return `${n.toFixed(1)} km`;
}

const UZ_MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
  'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr'];

export function relTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return 'hozirgina';
  if (diff < 3600) return `${Math.floor(diff / 60)} daqiqa oldin`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} soat oldin`;
  if (diff < 172800) return 'kecha';
  return `${d.getDate()} ${UZ_MONTHS[d.getMonth()]}`;
}

// Buyurtma holati — yo'l/o'lchagich bekatlari (happy path)
export const STATUS_FLOW = ['PENDING', 'ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS', 'COMPLETED'];

export const STATUS_LABELS = {
  PENDING:     'Yuborildi',
  ACCEPTED:    'Qabul qilindi',
  ON_THE_WAY:  "Yo'lda",
  IN_PROGRESS: 'Ish jarayonida',
  COMPLETED:   'Yakunlandi',
  CANCELLED:   'Bekor qilindi',
  REJECTED:    'Rad etildi',
};

export const STATUS_TONE = {
  PENDING: 'amber', ACCEPTED: 'cobalt', ON_THE_WAY: 'amber',
  IN_PROGRESS: 'cobalt', COMPLETED: 'success',
  CANCELLED: 'danger', REJECTED: 'danger',
};

export function ratingText(value) {
  const n = Number(value || 0);
  return n > 0 ? n.toFixed(1) : 'yangi';
}
