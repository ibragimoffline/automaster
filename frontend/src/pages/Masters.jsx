import { useEffect, useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, SlidersHorizontal, Car, Map, List, Frown } from 'lucide-react';
import MasterCard from '../components/MasterCard';
import RadarLocator from '../components/RadarLocator';
import { api } from '../api/client';
import { MOCK_MASTERS } from '../lib/mock';

const SORTS = [
  { key: 'distance', label: 'Yaqinlik' },
  { key: 'rating', label: 'Reyting' },
  { key: 'experience', label: 'Tajriba' },
];

export default function Masters() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const [all, setAll] = useState(MOCK_MASTERS);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(true);

  const [q, setQ] = useState(params.get('q') || '');
  const [visiting, setVisiting] = useState(false);
  const [verified, setVerified] = useState(false);
  const [sort, setSort] = useState('distance');
  const [view, setView] = useState('list'); // list | map (mobil)

  useEffect(() => {
    setLoading(true);
    api.nearbyMasters({ lat: 41.31, lng: 69.27, ...(visiting ? { visiting: 'true' } : {}) })
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        if (list?.length) { setAll(list); setDemo(false); }
        else { setAll(MOCK_MASTERS); setDemo(true); }
      })
      .catch(() => { setAll(MOCK_MASTERS); setDemo(true); })
      .finally(() => setLoading(false));
  }, [visiting]);

  const filtered = useMemo(() => {
    let list = [...all];
    if (verified) list = list.filter((m) => m.is_verified);
    if (visiting) list = list.filter((m) => m.can_visit_customer);
    if (q.trim()) {
      const t = q.toLowerCase();
      list = list.filter((m) =>
        (m.full_name || '').toLowerCase().includes(t) ||
        (m.bio || '').toLowerCase().includes(t) ||
        (m.specialties || []).some((s) => s.toLowerCase().includes(t)) ||
        (m.workshop?.name || '').toLowerCase().includes(t)
      );
    }
    list.sort((a, b) => {
      if (sort === 'rating') return (b.average_rating || 0) - (a.average_rating || 0);
      if (sort === 'experience') return (b.experience_years || 0) - (a.experience_years || 0);
      return (a.distance_km || 99) - (b.distance_km || 99);
    });
    return list;
  }, [all, q, verified, visiting, sort]);

  return (
    <div className="masters">
      <div className="masters__bar">
        <div className="container masters__bar-inner">
          <form className="searchbar searchbar--inline" onSubmit={(e) => { e.preventDefault(); setParams(q ? { q } : {}); }} role="search">
            <div className="searchbar__field">
              <Search size={18} strokeWidth={2.2} />
              <input className="searchbar__input" placeholder="Xizmat yoki usta nomi" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Qidirish" />
            </div>
            <button className="btn btn--sm" type="submit">Qidirish</button>
          </form>

          <div className="masters__filters" role="group" aria-label="Filtrlar">
            <button className={`pill ${visiting ? 'is-on' : ''}`} onClick={() => setVisiting((v) => !v)} aria-pressed={visiting}>
              <Car size={15} /> Chiqib boradi
            </button>
            <button className={`pill ${verified ? 'is-on' : ''}`} onClick={() => setVerified((v) => !v)} aria-pressed={verified}>
              Tekshirilgan
            </button>
            <span className="masters__sort">
              <SlidersHorizontal size={15} />
              <select className="masters__sort-select" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Saralash">
                {SORTS.map((s) => <option key={s.key} value={s.key}>{s.label} bo'yicha</option>)}
              </select>
            </span>
          </div>
        </div>
      </div>

      <div className="container masters__layout">
        <div className={`masters__list ${view === 'map' ? 'is-hidden-mobile' : ''}`}>
          <div className="masters__count">
            <span><strong className="mono">{filtered.length}</strong> usta topildi</span>
            {demo && <span className="badge badge--muted">demo ma'lumotlari</span>}
            <div className="masters__viewtoggle">
              <button className={view === 'list' ? 'is-on' : ''} onClick={() => setView('list')} aria-label="Ro'yxat"><List size={16} /></button>
              <button className={view === 'map' ? 'is-on' : ''} onClick={() => setView('map')} aria-label="Xarita"><Map size={16} /></button>
            </div>
          </div>

          {loading ? (
            <div className="masters__grid">
              {[0, 1, 2, 3].map((i) => <div key={i} className="card mcard mcard--skel"><div className="skeleton" style={{ height: 150 }} /></div>)}
            </div>
          ) : filtered.length ? (
            <div className="masters__grid">
              {filtered.map((m) => <MasterCard key={m.id} master={m} />)}
            </div>
          ) : (
            <div className="empty">
              <span className="empty__icon"><Frown size={26} /></span>
              <strong>Hech narsa topilmadi</strong>
              <span>Filtrlarni o'zgartiring yoki boshqa xizmat nomini kiriting.</span>
              <button className="btn btn--ghost btn--sm" onClick={() => { setQ(''); setVisiting(false); setVerified(false); setParams({}); }}>Filtrlarni tozalash</button>
            </div>
          )}
        </div>

        <aside className={`masters__map ${view === 'list' ? 'is-hidden-mobile' : ''}`}>
          <div className="masters__map-card card">
            <div className="masters__map-head">
              <span className="eyebrow">Lokator</span>
              <span className="mono masters__map-radius">5 km</span>
            </div>
            <RadarLocator masters={filtered} onPick={(m) => navigate(`/masters/${m.id}`)} />
            <p className="masters__map-note">Pin ustiga bosing — usta profilini ko'rasiz. Markaz — sizning joylashuvingiz.</p>
          </div>
        </aside>
      </div>
    </div>
  );
}
