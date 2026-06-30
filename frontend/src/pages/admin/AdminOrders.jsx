import { useEffect, useState, useCallback } from 'react';
import { Search, Trash2 } from 'lucide-react';
import { api } from '../../api/client';
import { useToast } from '../../components/Toast';
import { soum, relTime, STATUS_LABELS } from '../../lib/format';

const STATUSES = ['PENDING', 'ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'REJECTED'];

export default function AdminOrders() {
  const toast = useToast();
  const [orders, setOrders] = useState(null);
  const [status, setStatus] = useState('');
  const [q, setQ] = useState('');

  const load = useCallback(() => {
    setOrders(null);
    const params = {};
    if (status) params.status = status;
    if (q.trim()) params.search = q.trim();
    api.adminOrders(params)
      .then((d) => setOrders(Array.isArray(d) ? d : d.results || []))
      .catch(() => { setOrders([]); toast.error('Buyurtmalar yuklanmadi'); });
  }, [status, q, toast]);

  useEffect(() => { load(); }, [status]); // eslint-disable-line

  const changeStatus = async (o, newStatus) => {
    try {
      const updated = await api.adminUpdateOrder(o.id, { status: newStatus });
      setOrders((list) => list.map((x) => (x.id === o.id ? { ...x, ...updated } : x)));
      toast.success(`#${o.id} → ${STATUS_LABELS[newStatus]}`);
    } catch (e) { toast.error(e.message || 'O\'zgartirib bo\'lmadi'); }
  };

  const remove = async (o) => {
    if (!window.confirm(`#${o.id} buyurtmasini o'chirasizmi?`)) return;
    try {
      await api.adminDeleteOrder(o.id);
      setOrders((list) => list.filter((x) => x.id !== o.id));
      toast.success('Buyurtma o\'chirildi');
    } catch (e) { toast.error(e.message || 'O\'chirib bo\'lmadi'); }
  };

  return (
    <div className="apage">
      <div className="apage__bar">
        <form className="apage__search" onSubmit={(e) => { e.preventDefault(); load(); }}>
          <Search size={16} />
          <input placeholder="Tavsif, mijoz yoki usta" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Qidirish" />
        </form>
        <select className="aselect aselect--lg" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Holat bo'yicha">
          <option value="">Barcha holatlar</option>
          {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
        </select>
      </div>

      {orders === null ? (
        <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />
      ) : (
        <div className="atable-wrap card">
          <table className="atable">
            <thead>
              <tr>
                <th>#</th><th>Muammo</th><th>Mijoz</th><th>Usta</th>
                <th>Holat</th><th className="ta-r">Narx</th><th>Sana</th><th></th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td className="mono">#{o.id}</td>
                  <td className="acell-desc">{o.problem_description}</td>
                  <td>{o.customer_username}<br /><span className="acell-sub mono">{o.customer_phone}</span></td>
                  <td>{o.master_name || <span className="acell-sub">—</span>}</td>
                  <td>
                    <select className="aselect" value={o.status} onChange={(e) => changeStatus(o, e.target.value)}>
                      {STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                    </select>
                  </td>
                  <td className="ta-r mono">{soum(o.final_price || o.offered_price)}</td>
                  <td className="mono acell-sub">{relTime(o.created_at)}</td>
                  <td className="ta-r">
                    <button className="aicon-btn aicon-btn--danger" title="O'chirish" onClick={() => remove(o)}><Trash2 size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {orders.length === 0 && <div className="empty"><strong>Topilmadi</strong></div>}
        </div>
      )}
    </div>
  );
}
