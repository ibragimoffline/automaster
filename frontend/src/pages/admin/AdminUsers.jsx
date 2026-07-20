import { useEffect, useState, useCallback } from 'react';
import { Search, Trash2, BadgeCheck, ShieldCheck } from 'lucide-react';
import { api } from '../../api/client';
import { useToast } from '../../components/Toast';
import { useAuth } from '../../auth/AuthContext';

const ROLES = [
  { v: 'CUSTOMER', label: 'Mijoz' },
  { v: 'MASTER', label: 'Usta' },
  { v: 'ADMIN', label: 'Admin' },
];
const ROLE_LABEL = Object.fromEntries(ROLES.map((r) => [r.v, r.label]));

export default function AdminUsers() {
  const toast = useToast();
  const { user: me } = useAuth();
  const [users, setUsers] = useState(null);
  const [role, setRole] = useState('');
  const [q, setQ] = useState('');

  const load = useCallback(() => {
    setUsers(null);
    const params = {};
    if (role) params.role = role;
    if (q.trim()) params.search = q.trim();
    api.adminUsers(params)
      .then((d) => setUsers(Array.isArray(d) ? d : d.results || []))
      .catch(() => { setUsers([]); toast.error('Foydalanuvchilar yuklanmadi'); });
  }, [role, q, toast]);

  useEffect(() => { load(); }, [role]);

  const patch = async (u, body, okMsg) => {
    try {
      const updated = await api.adminUpdateUser(u.id, body);
      setUsers((list) => list.map((x) => (x.id === u.id ? { ...x, ...updated } : x)));
      if (okMsg) toast.success(okMsg);
    } catch (e) { toast.error(e.message || 'O\'zgartirib bo\'lmadi'); }
  };

  const remove = async (u) => {
    if (!window.confirm(`${u.username} hisobini o'chirasizmi? Bu amalni qaytarib bo'lmaydi.`)) return;
    try {
      await api.adminDeleteUser(u.id);
      setUsers((list) => list.filter((x) => x.id !== u.id));
      toast.success('Foydalanuvchi o\'chirildi');
    } catch (e) { toast.error(e.message || 'O\'chirib bo\'lmadi'); }
  };

  return (
    <div className="apage">
      <div className="apage__bar">
        <form className="apage__search" onSubmit={(e) => { e.preventDefault(); load(); }}>
          <Search size={16} />
          <input placeholder="Ism, telefon yoki login" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Qidirish" />
        </form>
        <div className="apage__filters">
          <button className={`pill ${role === '' ? 'is-on' : ''}`} onClick={() => setRole('')}>Hammasi</button>
          {ROLES.map((r) => (
            <button key={r.v} className={`pill ${role === r.v ? 'is-on' : ''}`} onClick={() => setRole(r.v)}>{r.label}</button>
          ))}
        </div>
      </div>

      {users === null ? (
        <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />
      ) : (
        <div className="atable-wrap card">
          <table className="atable">
            <thead>
              <tr>
                <th>Foydalanuvchi</th><th>Telefon</th><th>Rol</th>
                <th className="ta-c">Tasdiq</th><th className="ta-c">Aktiv</th>
                <th className="ta-c">Buyurtma</th><th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className="acell-user">
                      <span className="acell-avatar">{(u.first_name || u.username)[0]?.toUpperCase()}</span>
                      <div>
                        <strong>{u.first_name || u.username}{u.is_master_verified && <BadgeCheck size={14} className="acell-verified" />}</strong>
                        <span className="acell-sub mono">@{u.username}</span>
                      </div>
                    </div>
                  </td>
                  <td className="mono">{u.phone}</td>
                  <td>
                    <select className="aselect" value={u.role}
                      disabled={u.id === me?.id}
                      onChange={(e) => patch(u, { role: e.target.value }, 'Rol o\'zgartirildi')}>
                      {ROLES.map((r) => <option key={r.v} value={r.v}>{r.label}</option>)}
                    </select>
                  </td>
                  <td className="ta-c">
                    <button className={`atoggle ${u.phone_verified ? 'is-on' : ''}`} title="Telefon tasdig'i"
                      onClick={() => patch(u, { phone_verified: !u.phone_verified })}>
                      <span /></button>
                  </td>
                  <td className="ta-c">
                    <button className={`atoggle ${u.is_active ? 'is-on' : ''}`} title="Aktiv holat"
                      disabled={u.id === me?.id}
                      onClick={() => patch(u, { is_active: !u.is_active })}>
                      <span /></button>
                  </td>
                  <td className="ta-c mono">{u.orders_count ?? 0}</td>
                  <td className="ta-r">
                    <button className="aicon-btn aicon-btn--danger" title="O'chirish"
                      disabled={u.id === me?.id || u.is_superuser}
                      onClick={() => remove(u)}><Trash2 size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && <div className="empty"><strong>Topilmadi</strong></div>}
        </div>
      )}
    </div>
  );
}
