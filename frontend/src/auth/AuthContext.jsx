import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api, tokens } from '../api/client';

const AuthCtx = createContext(null);

// JWT access tokenidan foydalanuvchi ma'lumotini o'qish (payloadni dekodlash)
function decode(access) {
  try {
    const payload = JSON.parse(atob(access.split('.')[1]));
    return payload;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (!tokens.access) return null;
    const p = decode(tokens.access);
    return p ? loadProfile() : null;
  });

  function loadProfile() {
    try { return JSON.parse(localStorage.getItem('am_user') || 'null'); }
    catch { return null; }
  }

  const persist = useCallback((u) => {
    if (u) localStorage.setItem('am_user', JSON.stringify(u));
    else localStorage.removeItem('am_user');
    setUser(u);
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await api.login(username, password);
    tokens.set(res);
    const payload = decode(res.access) || {};
    const u = { username, role: payload.role || 'CUSTOMER', phone_verified: payload.phone_verified ?? false, id: payload.user_id };
    persist(u);
    return u;
  }, [persist]);

  const register = useCallback(async (payload) => {
    // Register javobi to'g'ridan-to'g'ri tokenlar + foydalanuvchi ma'lumotini qaytaradi.
    const res = await api.register(payload);
    if (res?.tokens) {
      tokens.set(res.tokens);
      const u = { id: res.id, username: res.username, role: res.role || 'CUSTOMER', phone_verified: res.phone_verified ?? false };
      persist(u);
      return u;
    }
    return login(payload.username, payload.password);
  }, [login, persist]);

  const verifyPhone = useCallback(async () => {
    await api.verifyPhone();
    persist({ ...(user || {}), phone_verified: true });
  }, [user, persist]);

  const logout = useCallback(() => {
    tokens.clear();
    persist(null);
  }, [persist]);

  useEffect(() => {
    // Sahifa ochilganda access muddatini jimgina yangilashga urinish
    if (tokens.refresh && !tokens.access) api.refresh().catch(() => {});
  }, []);

  const value = { user, isAuthed: !!user, login, register, logout, verifyPhone, setUser: persist };
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
