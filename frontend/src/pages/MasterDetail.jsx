import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  BadgeCheck, MapPin, Clock, Car, ArrowLeft, Wrench, Lock, ShieldCheck, ChevronRight,
} from 'lucide-react';
import RatingStars from '../components/RatingStars';
import { priceRange, relTime, km } from '../lib/format';
import { getMockMaster, MOCK_SERVICES, MOCK_REVIEWS } from '../lib/mock';
import { api } from '../api/client';

export default function MasterDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [master, setMaster] = useState(() => getMockMaster(id) || null);
  const [reviews, setReviews] = useState([]);
  const [services, setServices] = useState(MOCK_SERVICES);

  useEffect(() => {
    api.master(id)
      .then((m) => { if (m) setMaster(m); })
      .catch(() => { if (!master) setMaster(getMockMaster(id) || getMockMaster(1)); });

    api.masterServices(id)
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        setServices(list?.length ? list : MOCK_SERVICES);
      })
      .catch(() => setServices(MOCK_SERVICES));

    api.reviews(id)
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        setReviews(list?.length
          ? list.map((r) => ({ ...r, customer_name: r.customer_username }))
          : MOCK_REVIEWS);
      })
      .catch(() => setReviews(MOCK_REVIEWS));
  }, [id]);

  if (!master) return <div className="container section">Yuklanmoqda…</div>;
  const ws = master.workshop || {};

  return (
    <div className="mdetail">
      <div className="container">
        <Link to="/masters" className="backlink"><ArrowLeft size={16} /> Ustalar ro'yxati</Link>
      </div>

      <header className="mhero">
        <div className="container mhero__inner">
          <div className="mhero__avatar" aria-hidden="true">
            {master.full_name?.split(' ').map((w) => w[0]).slice(0, 2).join('')}
          </div>
          <div className="mhero__id">
            <div className="mhero__namerow">
              <h1 className="mhero__name">{master.full_name}</h1>
              {master.is_verified && <span className="badge badge--verified"><BadgeCheck /> Tekshirilgan</span>}
              {master.can_visit_customer && <span className="badge badge--visit"><Car /> Chiqib boradi</span>}
            </div>
            <div className="mhero__meta">
              <RatingStars value={master.average_rating} count={master.total_reviews} size={16} />
              <span className="mhero__dot" />
              <span className="mono"><Clock size={14} /> {master.experience_years}+ yil tajriba</span>
              {km(master.distance_km) && <><span className="mhero__dot" /><span className="mono"><MapPin size={14} /> {km(master.distance_km)}</span></>}
            </div>
            <p className="mhero__bio">{master.bio}</p>
          </div>
          <div className="mhero__cta">
            <Link to={`/orders/new?master=${master.id}`} className="btn btn--lg"><Wrench size={18} /> Buyurtma berish</Link>
            <div className="contact-locked contact-locked--cta">
              <Lock size={15} />
              <span>Aloqa ma'lumotlari buyurtma qabul qilingach ochiladi</span>
            </div>
          </div>
        </div>
      </header>

      <div className="container mdetail__grid">
        <div className="mdetail__main">
          <section className="block card">
            <h2 className="block__title">Xizmatlar va narxlar</h2>
            <ul className="svc-list">
              {services.map((s) => (
                <li key={s.id} className="svc">
                  <div className="svc__info">
                    <div className="svc__top">
                      <span className="svc__title">{s.title}</span>
                      <span className="badge badge--muted">{s.category_name}</span>
                    </div>
                    <p className="svc__desc">{s.description}</p>
                  </div>
                  <div className="svc__price">
                    <span className="mono svc__amount">{priceRange(s.price_from, s.price_to)}</span>
                    <Link to={`/orders/new?master=${master.id}`} className="svc__pick">Tanlash <ChevronRight size={15} /></Link>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section className="block card">
            <div className="block__head">
              <h2 className="block__title">Mijozlar sharhlari</h2>
              <RatingStars value={master.average_rating} count={master.total_reviews} size={15} />
            </div>
            <ul className="rev-list">
              {reviews.map((r) => (
                <li key={r.id} className="rev">
                  <div className="rev__top">
                    <span className="rev__avatar">{(r.customer_name || 'M')[0]}</span>
                    <div className="rev__who">
                      <strong>{r.customer_name || 'Mijoz'}</strong>
                      <span className="mono rev__date">{relTime(r.created_at)}</span>
                    </div>
                    <RatingStars value={r.rating} showValue={false} size={14} />
                  </div>
                  {r.comment && <p className="rev__text">{r.comment}</p>}
                </li>
              ))}
            </ul>
          </section>
        </div>

        <aside className="mdetail__side">
          <div className="block card wsbox">
            <h3 className="wsbox__name">{ws.name || 'Ustaxona'}</h3>
            <div className="wsbox__row"><MapPin size={16} /> {ws.region}, {ws.district}</div>
            {ws.open_time && <div className="wsbox__row"><Clock size={16} /> {ws.open_time}–{ws.close_time}</div>}
            <div className="wsbox__map" aria-hidden="true">
              <div className="wsbox__pin"><MapPin size={20} fill="var(--cobalt)" stroke="#fff" /></div>
              <span className="mono wsbox__coords">{ws.district || 'Toshkent'}</span>
            </div>
            <div className="wsbox__trust">
              <ShieldCheck size={16} /> Hujjatlari tekshirilgan
            </div>
          </div>
        </aside>
      </div>

      <div className="sticky-cta">
        <div>
          <span className="mono sticky-cta__rate">{Number(master.average_rating).toFixed(1)} ★</span>
          <span className="sticky-cta__name">{master.full_name}</span>
        </div>
        <Link to={`/orders/new?master=${master.id}`} className="btn"><Wrench size={17} /> Buyurtma</Link>
      </div>
    </div>
  );
}
