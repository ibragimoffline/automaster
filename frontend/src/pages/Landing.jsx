import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search, MapPin, ShieldCheck, Car, Wrench, Cog, Zap, Snowflake, Disc,
  Gauge, PaintBucket, CircleDot, ArrowRight, Star, Phone, ChevronRight, BadgeCheck,
} from 'lucide-react';
import RadarLocator from '../components/RadarLocator';
import MasterCard from '../components/MasterCard';
import { api } from '../api/client';
import { MOCK_CATEGORIES, MOCK_MASTERS } from '../lib/mock';

function pickIcon(name = '') {
  const n = name.toLowerCase();
  if (n.includes('dvigatel') || n.includes('moy')) return Cog;
  if (n.includes('elektr') || n.includes('akkum') || n.includes('generator')) return Zap;
  if (n.includes('konditsioner')) return Snowflake;
  if (n.includes('tormoz')) return Disc;
  if (n.includes('diagnost')) return Gauge;
  if (n.includes('kuzov') || n.includes('bo\'yoq')) return PaintBucket;
  if (n.includes('shina') || n.includes('xodovoy') || n.includes('razval')) return CircleDot;
  return Wrench;
}

const STEPS = [
  { t: 'Muammoni yozing', d: 'Nosozlikni tasvirlang, rasm biriktiring va joylashuvingizni belgilang.' },
  { t: 'Ustani tanlang', d: 'Yaqin atrofdagi tekshirilgan ustalarni reyting va narx bo\'yicha solishtiring.' },
  { t: 'Usta yetib keladi', d: 'Usta yo\'lga chiqadi yoki mashinani ustaxonaga olib boring — real vaqtda kuzating.' },
  { t: 'Baholang', d: 'Ish yakunlangach yakuniy narxni ko\'ring va ustaga sharh qoldiring.' },
];

export default function Landing() {
  const navigate = useNavigate();
  const [masters, setMasters] = useState(MOCK_MASTERS);
  const [categories, setCategories] = useState(MOCK_CATEGORIES);
  const [q, setQ] = useState('');

  useEffect(() => {
    api.nearbyMasters({ lat: 41.31, lng: 69.27 })
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        if (list?.length) setMasters(list);
      })
      .catch(() => {});
    api.categories()
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        if (list?.length) setCategories(list.slice(0, 8));
      })
      .catch(() => {});
  }, []);

  const submitSearch = (e) => {
    e.preventDefault();
    navigate(`/masters${q ? `?q=${encodeURIComponent(q)}` : ''}`);
  };

  return (
    <div className="landing">
      <section className="hero">
        <div className="container hero__grid">
          <div className="hero__copy">
            <span className="eyebrow hero__eyebrow">
              <span className="hero__live" /> Toshkent · {masters.length} usta onlayn
            </span>
            <h1 className="hero__title">
              Mashinangiz to'xtab qoldimi?<br />
              <span className="hero__title-accent">Usta allaqachon yaqin atrofda.</span>
            </h1>
            <p className="hero__lede">
              Yaqin atrofdagi tekshirilgan avto-ustani toping, narxni oldindan biling
              va ustani o'zingizga chaqiring — yoki ustaxonaga boring.
            </p>

            <form className="searchbar" onSubmit={submitSearch} role="search">
              <div className="searchbar__field">
                <Search size={19} strokeWidth={2.2} />
                <input
                  className="searchbar__input"
                  placeholder="Qaysi xizmat kerak? (masalan: dvigatel, tormoz)"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  aria-label="Xizmatni qidirish"
                />
              </div>
              <div className="searchbar__loc">
                <MapPin size={17} strokeWidth={2.2} /> Yunusobod
              </div>
              <button className="btn searchbar__btn" type="submit">
                Topish <ArrowRight size={18} strokeWidth={2.4} />
              </button>
            </form>

            <ul className="hero__chips" aria-label="Mashhur qidiruvlar">
              {['Dvigatel diagnostikasi', 'Moy almashtirish', 'Konditsioner', 'Shina'].map((c) => (
                <li key={c}>
                  <button className="chip" onClick={() => navigate(`/masters?q=${encodeURIComponent(c)}`)}>
                    {c}
                  </button>
                </li>
              ))}
            </ul>

            <div className="hero__trust">
              <span className="mono"><strong>2 400+</strong> tekshirilgan usta</span>
              <span className="hero__dot" />
              <span className="mono"><Star size={13} fill="var(--amber)" stroke="var(--amber)" /> <strong>4.8</strong> o'rtacha reyting</span>
              <span className="hero__dot" />
              <span className="mono"><strong>~14 daq</strong> javob vaqti</span>
            </div>
          </div>

          <div className="hero__radar">
            <div className="hero__radar-card card">
              <div className="hero__radar-head">
                <span className="eyebrow">Yaqin atrofda</span>
                <span className="badge badge--verified"><BadgeCheck /> Jonli</span>
              </div>
              <RadarLocator masters={masters} onPick={(m) => navigate(`/masters/${m.id}`)} />
              <div className="hero__radar-foot">
                <span className="mono">5 km radius</span>
                <Link to="/masters" className="hero__radar-link">Hammasi <ChevronRight size={15} /></Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section cats">
        <div className="container">
          <div className="sec-head">
            <div>
              <span className="eyebrow">Xizmat turlari</span>
              <h2 className="sec-title">Nima nosoz?</h2>
            </div>
            <Link to="/masters" className="sec-link">Barcha ustalar <ArrowRight size={16} /></Link>
          </div>
          <div className="cats__grid">
            {categories.map((c) => {
              const Icon = pickIcon(c.name);
              const count = c.master_count ?? c.count;
              return (
                <Link key={c.id} to={`/masters?q=${encodeURIComponent(c.name)}`} className="catcard card">
                  <span className="catcard__icon"><Icon size={22} strokeWidth={2} /></span>
                  <span className="catcard__name">{c.name}</span>
                  {count != null && <span className="catcard__count mono">{count} usta</span>}
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section how" id="qanday">
        <div className="container">
          <div className="sec-head sec-head--center">
            <span className="eyebrow">To'rt qadam</span>
            <h2 className="sec-title">Buzilishdan tuzatishgacha</h2>
          </div>
          <ol className="how__grid">
            {STEPS.map((s, i) => (
              <li key={i} className="how__step">
                <span className="how__num mono">{String(i + 1).padStart(2, '0')}</span>
                <h3 className="how__t">{s.t}</h3>
                <p className="how__d">{s.d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="section feat">
        <div className="container">
          <div className="sec-head">
            <div>
              <span className="eyebrow">Eng yaxshilar</span>
              <h2 className="sec-title">Yaqin atrofdagi ustalar</h2>
            </div>
            <Link to="/masters" className="sec-link">Hammasi <ArrowRight size={16} /></Link>
          </div>
          <div className="feat__grid">
            {masters.slice(0, 3).map((m) => <MasterCard key={m.id} master={m} />)}
          </div>
        </div>
      </section>

      <section className="section trust" id="trust">
        <div className="container trust__inner">
          <div className="trust__copy">
            <span className="eyebrow" style={{ color: 'var(--amber)' }}>Nega Automaster</span>
            <h2 className="trust__title">Har bir usta tekshiruvdan o'tadi.</h2>
            <p className="trust__lede">
              Telefon tasdig'i, hujjat tekshiruvi va real mijozlar sharhlari —
              ishingizni faqat ishonchli qo'llarga topshiring.
            </p>
            <div className="trust__list">
              {[
                { icon: ShieldCheck, t: 'Tekshirilgan ustalar', d: 'Hujjat va telefon tasdig\'i' },
                { icon: Star, t: 'Haqiqiy sharhlar', d: 'Faqat yakunlangan buyurtmalardan' },
                { icon: Car, t: 'Chiqib borish', d: 'Usta o\'zi yoningizga keladi' },
                { icon: Gauge, t: 'Shaffof narx', d: 'Ishdan oldin narxni biling' },
              ].map(({ icon: Icon, t, d }) => (
                <div key={t} className="trust__item">
                  <span className="trust__ic"><Icon size={20} strokeWidth={2.1} /></span>
                  <div><strong>{t}</strong><span>{d}</span></div>
                </div>
              ))}
            </div>
          </div>
          <div className="trust__panel card">
            <div className="trust__stat"><span className="mono trust__big">98.6%</span><span>buyurtmalar muvaffaqiyatli yakunlandi</span></div>
            <div className="trust__bars">
              {[5, 4, 3, 2, 1].map((s, i) => (
                <div key={s} className="trust__bar-row">
                  <span className="mono">{s}<Star size={11} fill="var(--amber)" stroke="var(--amber)" /></span>
                  <span className="trust__bar"><span style={{ width: [88, 9, 2, 0.6, 0.4][i] + '%' }} /></span>
                </div>
              ))}
            </div>
            <div className="trust__quote">
              "Yo'lda qoldim, 15 daqiqada usta yetib keldi. Narx ham aytilganidek."
              <span className="mono">— Aziz, Toshkent</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="cta">
            <div className="cta__copy">
              <span className="eyebrow" style={{ color: 'rgba(255,255,255,.6)' }}>Ustalar uchun</span>
              <h2 className="cta__title">Mijozlar sizni qidiryapti.</h2>
              <p className="cta__lede">Ustaxonangizni ro'yxatga qo'shing, yangi buyurtmalar oling va o'z jadvalingiz bo'yicha ishlang.</p>
            </div>
            <div className="cta__actions">
              <Link to="/register" className="btn btn--amber btn--lg">Usta bo'lib qo'shilish</Link>
              <a href="tel:+998711234567" className="btn btn--onink btn--lg"><Phone size={18} /> Biz bilan bog'lanish</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
