import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ClipboardList, ChevronRight, Plus, Car, Inbox, CheckCircle2 } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { MOCK_ORDERS } from '../lib/mock';
import { soum, relTime, STATUS_FLOW } from '../lib/format';

const ACTIVE = ['PENDING', 'ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS'];

export default function Orders() {
  const { user } = useAuth();
  const isMaster = user?.role === 'MASTER';
  const [params, setParams] = useSearchParams();
  const tab = params.get('tab') === 'history' ? 'history' : 'active';

  const [orders, setOrders] = useState(null);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    api.myOrders()
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results || [];
        if (list.length) { setOrders(list); setDemo(false); }
        else { setOrders(isMaster ? [] : MOCK_ORDERS); setDemo(!isMaster); }
      })
      .catch(() => { setOrders(isMaster ? [] : MOCK_ORDERS); setDemo(!isMaster); });
  }, [isMaster]);

  const shown = useMemo(() => {
    if (!orders) return null;
    if (!isMaster) return orders;
    return orders.filter((o) =>
      tab === 'active' ? ACTIVE.includes(o.status) : !ACTIVE.includes(o.status));
  }, [orders, isMaster, tab]);

  const setTab = (t) => setParams(t === 'history' ? { tab: 'history' } : {});

  return (
    <div className="container orders">
      <div className="orders__head">
        <div>
          <span className="eyebrow">Buyurtmalar</span>
          <h1 className="orders__title">{isMaster ? 'Kelgan buyurtmalar' : 'Mening buyurtmalarim'}</h1>
        </div>
        {!isMaster && <Link to="/orders/new" className="btn"><Plus size={17} /> Yangi buyurtma</Link>}
      </div>

      {isMaster && (
        <div className="otabs" role="tablist" aria-label="Buyurtma holati">
          <button role="tab" aria-selected={tab === 'active'} className={`otab ${tab === 'active' ? 'is-on' : ''}`} onClick={() => setTab('active')}>
            <Inbox size={16} /> Faol
          </button>
          <button role="tab" aria-selected={tab === 'history'} className={`otab ${tab === 'history' ? 'is-on' : ''}`} onClick={() => setTab('history')}>
            <CheckCircle2 size={16} /> Tarix
          </button>
        </div>
      )}

      {demo && <span className="badge badge--muted orders__demo">demo ma'lumotlari</span>}

      {shown === null ? (
        <div className="orders__list">
          {[0, 1].map((i) => <div key={i} className="card orders__row"><div className="skeleton" style={{ height: 64 }} /></div>)}
        </div>
      ) : shown.length === 0 ? (
        <EmptyState isMaster={isMaster} tab={tab} />
      ) : (
        <ul className="orders__list">
          {shown.map((o) => {
            const idx = STATUS_FLOW.indexOf(o.status);
            const pct = idx <= 0 ? 6 : (idx / (STATUS_FLOW.length - 1)) * 100;
            return (
              <li key={o.id}>
                <Link to={`/orders/${o.id}`} className="card orders__row">
                  <div className="orders__row-main">
                    <div className="orders__row-top">
                      <span className="mono orders__id">#{o.id}</span>
                      <StatusBadge status={o.status} />
                      {o.need_master_visit && <span className="badge badge--visit"><Car /> Chiqib kelish</span>}
                    </div>
                    <p className="orders__desc">{o.problem_description}</p>
                    <div className="orders__meta">
                      <span>{isMaster ? (o.customer_username || 'Mijoz') : (o.master_name || o.master?.full_name || 'Usta tanlanmagan')}</span>
                      <span className="orders__dot" />
                      <span className="mono">{relTime(o.created_at)}</span>
                      <span className="orders__dot" />
                      <span className="mono">{soum(o.final_price || o.offered_price)}</span>
                    </div>
                    <div className="orders__mini-track" aria-hidden="true">
                      <span style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                  <ChevronRight size={20} className="orders__chev" />
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function EmptyState({ isMaster, tab }) {
  if (isMaster) {
    return (
      <div className="empty">
        <span className="empty__icon">{tab === 'history' ? <CheckCircle2 size={26} /> : <Inbox size={26} />}</span>
        <strong>{tab === 'history' ? 'Tarix hozircha bo\'sh' : 'Faol buyurtmalar yo\'q'}</strong>
        <span>{tab === 'history'
          ? 'Yakunlangan va bekor qilingan buyurtmalar shu yerda ko\'rinadi.'
          : 'Sizga yangi buyurtma kelganda shu yerda paydo bo\'ladi.'}</span>
      </div>
    );
  }
  return (
    <div className="empty">
      <span className="empty__icon"><ClipboardList size={26} /></span>
      <strong>Hali buyurtmangiz yo'q</strong>
      <span>Birinchi buyurtmani bering — yaqin atrofdagi usta darhol xabar oladi.</span>
      <Link to="/orders/new" className="btn"><Plus size={16} /> Usta chaqirish</Link>
    </div>
  );
}
