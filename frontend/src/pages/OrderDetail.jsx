import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, MapPin, Car, Phone, Send, MessageSquare, Loader2, Check,
  ShieldCheck, Flag, User, Lock,
} from 'lucide-react';
import ServiceTrack from '../components/ServiceTrack';
import StatusBadge from '../components/StatusBadge';
import RatingStars from '../components/RatingStars';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../components/Toast';
import { getMockOrder } from '../lib/mock';
import { soum, relTime } from '../lib/format';

const MASTER_ACTIVE = ['ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS'];

export default function OrderDetail() {
  const { id } = useParams();
  const toast = useToast();
  const { user } = useAuth();
  const isMaster = user?.role === 'MASTER';
  const [order, setOrder] = useState(() => getMockOrder(id) || null);
  const [demo, setDemo] = useState(false);

  // Mijoz: sharh holati
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [sending, setSending] = useState(false);
  const [reviewed, setReviewed] = useState(false);

  // Usta: amal holati
  const [acting, setActing] = useState(false);
  const [finalPrice, setFinalPrice] = useState('');

  useEffect(() => {
    api.order(id)
      .then((o) => { if (o) { setOrder(o); setDemo(false); } })
      .catch(() => { const m = getMockOrder(id); if (m) { setOrder(m); setDemo(true); } });
  }, [id]);

  if (!order) return <div className="container section">Buyurtma topilmadi.</div>;

  const masterName = order.master_name || order.master?.full_name || 'Usta tayinlanmagan';
  const wsName = order.master?.workshop_name || order.master?.workshop?.name;
  const customerName = order.customer_username || 'Mijoz';

  const submitReview = async () => {
    if (!rating) { toast.error('Iltimos, baho bering'); return; }
    setSending(true);
    try {
      await api.createReview({ order: order.id, rating, comment });
      toast.success('Sharhingiz uchun rahmat!');
      setReviewed(true);
    } catch (err) {
      if (demo) { toast.success('Sharh qabul qilindi (demo)'); setReviewed(true); }
      else toast.error(err.message || 'Sharh yuborilmadi');
    } finally { setSending(false); }
  };

  const acceptOrder = async () => {
    setActing(true);
    try {
      const o = await api.acceptOrder(order.id);
      setOrder(o); toast.success('Buyurtma qabul qilindi');
    } catch (err) { toast.error(err.message || 'Qabul qilib bo\'lmadi'); }
    finally { setActing(false); }
  };

  const completeOrder = async () => {
    setActing(true);
    try {
      const o = await api.completeOrder(order.id, finalPrice || order.offered_price || null);
      setOrder(o); toast.success('Buyurtma yakunlandi');
    } catch (err) { toast.error(err.message || 'Yakunlab bo\'lmadi'); }
    finally { setActing(false); }
  };

  return (
    <div className="container odetail">
      <Link to="/orders" className="backlink">
        <ArrowLeft size={16} /> {isMaster ? 'Buyurtmalar' : 'Buyurtmalarim'}
      </Link>

      <div className="odetail__head">
        <div>
          <span className="mono odetail__id">BUYURTMA #{order.id}</span>
          <h1 className="odetail__title">{order.service_category_name || 'Avto-xizmat'}</h1>
          <span className="mono odetail__time">{relTime(order.created_at)}</span>
        </div>
        <StatusBadge status={order.status} />
      </div>

      {/* IMZO: holat o'lchagichi */}
      <section className="block card odetail__track">
        <ServiceTrack status={order.status} />
      </section>

      <div className="odetail__grid">
        <div className="stack" style={{ gap: 18 }}>
          <section className="block card">
            <h2 className="block__title">Muammo tafsiloti</h2>
            <p className="odetail__desc">{order.problem_description}</p>
            <div className="odetail__facts">
              <div className="fact"><MapPin size={16} /><span>{order.customer_address || 'Manzil ko\'rsatilmagan'}</span></div>
              <div className="fact"><Car size={16} /><span>{order.need_master_visit ? 'Usta manzilga chiqadi' : 'Ustaxonada xizmat'}</span></div>
            </div>
          </section>

          {/* USTA AMALLARI */}
          {isMaster && order.status === 'PENDING' && (
            <section className="block card oactions">
              <h2 className="block__title">Buyurtmani qabul qilasizmi?</h2>
              <p className="oactions__hint">Qabul qilsangiz, mijoz xabar oladi va siz bilan bog'lanadi.</p>
              <button className="btn btn--block" onClick={acceptOrder} disabled={acting}>
                {acting ? <><Loader2 size={16} className="spin" /> …</> : <><ShieldCheck size={17} /> Qabul qilish</>}
              </button>
            </section>
          )}
          {isMaster && MASTER_ACTIVE.includes(order.status) && (
            <section className="block card oactions">
              <h2 className="block__title">Ishni yakunlash</h2>
              <div className="field">
                <label htmlFor="fp">Yakuniy narx <span className="hint" style={{ fontWeight: 400 }}>(so'm)</span></label>
                <input id="fp" className="input mono" inputMode="numeric"
                  placeholder={String(order.offered_price || '150000')}
                  value={finalPrice} onChange={(e) => setFinalPrice(e.target.value.replace(/\D/g, ''))} />
                <span className="hint">Bo'sh qoldirsangiz, taklif qilingan narx ({soum(order.offered_price)}) qo'llanadi.</span>
              </div>
              <button className="btn btn--block" onClick={completeOrder} disabled={acting}>
                {acting ? <><Loader2 size={16} className="spin" /> …</> : <><Flag size={17} /> Yakunlandi deb belgilash</>}
              </button>
            </section>
          )}

          {/* MIJOZ SHARHI — faqat yakunlangan buyurtmaga */}
          {!isMaster && order.status === 'COMPLETED' && (
            <section className="block card">
              <h2 className="block__title"><MessageSquare size={18} style={{ verticalAlign: -3, marginRight: 6 }} /> Ustani baholang</h2>
              {reviewed ? (
                <div className="review-done"><Check size={18} /> Sharhingiz qabul qilindi. Rahmat!</div>
              ) : (
                <div className="stack" style={{ gap: 14 }}>
                  <RatingStars value={rating} interactive onRate={setRating} size={30} showValue={false} />
                  <div className="field">
                    <label htmlFor="cm">Izoh <span className="hint" style={{ fontWeight: 400 }}>(ixtiyoriy)</span></label>
                    <textarea id="cm" className="textarea" placeholder="Ish sifati, narx, muloqot haqida yozing…"
                      value={comment} onChange={(e) => setComment(e.target.value)} />
                  </div>
                  <button className="btn" onClick={submitReview} disabled={sending}>
                    {sending ? <><Loader2 size={16} className="spin" /> Yuborilmoqda…</> : <><Send size={16} /> Sharh yuborish</>}
                  </button>
                </div>
              )}
            </section>
          )}
        </div>

        {/* Yon panel — rolega qarab: usta uchun mijoz, mijoz uchun usta */}
        <aside className="stack" style={{ gap: 18 }}>
          {isMaster ? (
            <div className="block card omaster">
              <span className="eyebrow">Mijoz</span>
              <div className="omaster__row">
                <span className="omaster__avatar"><User size={18} /></span>
                <div>
                  <strong>{customerName}</strong>
                  <span className="omaster__ws">{order.customer_address || 'Manzil ko\'rsatilmagan'}</span>
                </div>
              </div>
              {order.contact_unlocked && order.customer_phone ? (
                <a href={`tel:${order.customer_phone}`} className="btn btn--ghost btn--block"><Phone size={16} /> {order.customer_phone}</a>
              ) : (
                <div className="contact-locked">
                  <Lock size={15} />
                  <span>{order.status === 'PENDING'
                    ? 'Qabul qilsangiz, mijoz aloqasi ochiladi'
                    : 'Aloqa ma\'lumotlari yopiq'}</span>
                </div>
              )}
            </div>
          ) : (
            <div className="block card omaster">
              <span className="eyebrow">Usta</span>
              <div className="omaster__row">
                <span className="omaster__avatar">{masterName.split(' ').map((w) => w[0]).slice(0, 2).join('')}</span>
                <div>
                  <strong>{masterName}</strong>
                  {wsName && <span className="omaster__ws">{wsName}</span>}
                </div>
              </div>
              {order.master?.average_rating && <RatingStars value={order.master.average_rating} size={14} />}
              {order.contact_unlocked && order.master_phone ? (
                <a href={`tel:${order.master_phone}`} className="btn btn--ghost btn--block"><Phone size={16} /> {order.master_phone}</a>
              ) : (
                <div className="contact-locked">
                  <Lock size={15} />
                  <span>{order.status === 'PENDING'
                    ? 'Usta qabul qilgach aloqa ochiladi'
                    : 'Aloqa ma\'lumotlari yopiq'}</span>
                </div>
              )}
            </div>
          )}

          <div className="block card oprice">
            <div className="oprice__row"><span>Taklif qilingan</span><span className="mono">{soum(order.offered_price)}</span></div>
            <div className="oprice__row oprice__row--final">
              <span>Yakuniy narx</span>
              <span className="mono oprice__final">{order.final_price ? soum(order.final_price) : '— kutilmoqda'}</span>
            </div>
          </div>
        </aside>
      </div>

      {demo && <span className="badge badge--muted" style={{ marginTop: 18 }}>demo ma'lumotlari</span>}
    </div>
  );
}
