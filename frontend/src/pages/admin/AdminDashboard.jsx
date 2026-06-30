import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Wrench, ClipboardList, Wallet, Star, ShieldCheck, ArrowRight } from 'lucide-react';
import StatusBadge from '../../components/StatusBadge';
import { api } from '../../api/client';
import { soum, relTime, STATUS_LABELS } from '../../lib/format';

const STATUS_COLORS = {
  PENDING: 'var(--amber)', ACCEPTED: 'var(--cobalt)', ON_THE_WAY: 'var(--amber)',
  IN_PROGRESS: 'var(--cobalt)', COMPLETED: 'var(--success)',
  CANCELLED: 'var(--danger)', REJECTED: 'var(--danger)',
};

export default function AdminDashboard() {
  const [s, setS] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    api.adminStats().then(setS).catch(() => setErr(true));
  }, []);

  if (err) return <div className="empty"><strong>Statistika yuklanmadi</strong></div>;
  if (!s) return <div className="adash__cards">{[0,1,2,3].map(i => <div key={i} className="card astat"><div className="skeleton" style={{height:64}} /></div>)}</div>;

  const cards = [
    { icon: Users, label: 'Foydalanuvchilar', value: s.users.total, sub: `${s.users.customers} mijoz · ${s.users.masters} usta`, to: '/admin/users' },
    { icon: Wrench, label: 'Ustalar', value: s.masters.total, sub: `${s.masters.verified} tekshirilgan`, to: '/admin/masters' },
    { icon: ClipboardList, label: 'Buyurtmalar', value: s.orders.total, sub: `${s.orders.by_status.COMPLETED || 0} yakunlangan`, to: '/admin/orders' },
    { icon: Wallet, label: 'Aylanma', value: soum(s.revenue), sub: 'yakunlangan ishlardan', mono: true },
  ];
  const total = s.orders.total || 1;

  return (
    <div className="adash">
      <div className="adash__cards">
        {cards.map((c) => {
          const Inner = (
            <>
              <span className="astat__icon"><c.icon size={20} strokeWidth={2.1} /></span>
              <span className={`astat__value ${c.mono ? 'mono' : ''}`}>{c.value}</span>
              <span className="astat__label">{c.label}</span>
              <span className="astat__sub">{c.sub}</span>
            </>
          );
          return c.to
            ? <Link key={c.label} to={c.to} className="card astat astat--link">{Inner}</Link>
            : <div key={c.label} className="card astat">{Inner}</div>;
        })}
      </div>

      <div className="adash__grid">
        <section className="card adash__block">
          <h2 className="block__title">Buyurtmalar holati bo'yicha</h2>
          <div className="adash__bars">
            {Object.entries(s.orders.by_status).sort((a,b)=>b[1]-a[1]).map(([st, n]) => (
              <div key={st} className="adash__bar-row">
                <span className="adash__bar-label">{STATUS_LABELS[st] || st}</span>
                <span className="adash__bar"><span style={{ width: `${(n/total)*100}%`, background: STATUS_COLORS[st] }} /></span>
                <span className="mono adash__bar-n">{n}</span>
              </div>
            ))}
          </div>
          <div className="adash__mini">
            <span><ShieldCheck size={15} /> {s.masters.verified}/{s.masters.total} tekshirilgan usta</span>
            <span><Star size={15} /> {s.reviews} sharh</span>
          </div>
        </section>

        <section className="card adash__block">
          <div className="block__head">
            <h2 className="block__title">So'nggi buyurtmalar</h2>
            <Link to="/admin/orders" className="sec-link">Hammasi <ArrowRight size={15} /></Link>
          </div>
          <ul className="adash__recent">
            {s.recent_orders.map((o) => (
              <li key={o.id}>
                <Link to="/admin/orders" className="adash__recent-row">
                  <span className="mono adash__recent-id">#{o.id}</span>
                  <span className="adash__recent-desc">{o.problem_description}</span>
                  <StatusBadge status={o.status} />
                  <span className="mono adash__recent-time">{relTime(o.created_at)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
