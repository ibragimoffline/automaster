
const ACCESS = 'am_access';
const REFRESH = 'am_refresh';

export const tokens = {
  get access() { return localStorage.getItem(ACCESS); },
  get refresh() { return localStorage.getItem(REFRESH); },
  set({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  },
  clear() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH); },
};

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function firstError(data, fallback) {
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  const firstKey = Object.keys(data)[0];
  if (firstKey) {
    const v = data[firstKey];
    return Array.isArray(v) ? v[0] : String(v);
  }
  return fallback;
}

async function refreshAccess() {
  if (!tokens.refresh) return false;
  const res = await fetch('/api/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });
  if (!res.ok) { tokens.clear(); return false; }
  const data = await res.json();
  tokens.set({ access: data.access });
  return true;
}

async function request(path, { method = 'GET', body, auth = true, isForm = false, _retry = false } = {}) {
  const headers = {};
  if (!isForm) headers['Content-Type'] = 'application/json';
  if (auth && tokens.access) headers['Authorization'] = `Bearer ${tokens.access}`;

  const res = await fetch(path.startsWith('http') ? path : `/api${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth && !_retry && tokens.refresh) {
    const ok = await refreshAccess();
    if (ok) return request(path, { method, body, auth, isForm, _retry: true });
  }

  if (res.status === 204) return null;

  let data = null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new ApiError(firstError(data, `Xatolik (${res.status})`), res.status, data);
  }
  return data;
}

export const api = {
  login: (username, password) =>
    request('/token/', { method: 'POST', auth: false, body: { username, password } }),
  refresh: refreshAccess,
  register: (payload) =>
    request('/auth/register/', { method: 'POST', auth: false, body: payload }),
  verifyPhone: () => request('/auth/verify-phone/', { method: 'POST' }),

  nearbyMasters: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/masters/nearby/${q ? `?${q}` : ''}`, { auth: false });
  },
  master: (id) => request(`/masters/${id}/`, { auth: false }),
  masterComments: (id) => request(`/masters/${id}/comments/`, { auth: false }),
  masterLikeStatus: (id) => request(`/masters/${id}/like/`),
  toggleMasterLike: (id) => request(`/masters/${id}/like/`, { method: 'POST' }),

  categories: () => request('/services/categories/', { auth: false }),
  masterServices: (masterId) =>
    request(`/services/${masterId ? `?master=${masterId}` : ''}`, { auth: false }),

  ping: () => request('/masters/nearby/?lat=41.31&lng=69.27', { auth: false }),

  adminStats: () => request('/admin/stats/'),
  adminUsers: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/admin/users/${q ? `?${q}` : ''}`);
  },
  adminUpdateUser: (id, body) => request(`/admin/users/${id}/`, { method: 'PATCH', body }),
  adminDeleteUser: (id) => request(`/admin/users/${id}/`, { method: 'DELETE' }),
  adminMasters: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/admin/masters/${q ? `?${q}` : ''}`);
  },
  adminUpdateMaster: (id, body) => request(`/admin/masters/${id}/`, { method: 'PATCH', body }),
  adminOrders: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/admin/orders/${q ? `?${q}` : ''}`);
  },
  adminUpdateOrder: (id, body) => request(`/admin/orders/${id}/`, { method: 'PATCH', body }),
  adminDeleteOrder: (id) => request(`/admin/orders/${id}/`, { method: 'DELETE' }),
  adminCategories: () => request('/admin/categories/'),
  adminCreateCategory: (body) => request('/admin/categories/', { method: 'POST', body }),
  adminUpdateCategory: (id, body) => request(`/admin/categories/${id}/`, { method: 'PATCH', body }),
  adminDeleteCategory: (id) => request(`/admin/categories/${id}/`, { method: 'DELETE' }),
  adminReviews: () => request('/admin/reviews/'),
  adminDeleteReview: (id) => request(`/admin/reviews/${id}/`, { method: 'DELETE' }),

  myOrders: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/orders/${q ? `?${q}` : ''}`);
  },
  order: (id) => request(`/orders/${id}/`),
  createOrder: (payload) => request('/orders/', { method: 'POST', body: payload }),
  acceptOrder: (id) => request(`/orders/${id}/accept/`, { method: 'POST' }),
  completeOrder: (id, final_price) =>
    request(`/orders/${id}/complete/`, { method: 'POST', body: { final_price } }),

  reviews: (masterId) => request(`/reviews/${masterId ? `?master=${masterId}` : ''}`, { auth: false }),
  createReview: (payload) => request('/reviews/', { method: 'POST', body: payload }),
};

export { ApiError };
