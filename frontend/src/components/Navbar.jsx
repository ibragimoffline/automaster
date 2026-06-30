import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { MapPin, ClipboardList, LogOut, User, ChevronDown, Wrench, Shield } from 'lucide-react';
import Logo from './Logo';
import { api } from '../api/client';
import { useAuth } from '../auth/AuthContext';

const REGIONS = ['Toshkent', 'Samarqand', 'Buxoro', 'Andijon', 'Farg\'ona', 'Namangan'];

// Backend ulanganini ko'rsatuvchi kichik indikator
function ApiStatus() {
  const [state, setState] = useState('checking'); // checking | online | demo
  useEffect(() => {
    let alive = true;
    api.ping()
      .then((data) => { if (alive) setState(Array.isArray(data) && data.length ? 'online' : 'demo'); })
      .catch(() => { if (alive) setState('demo'); });
    return () => { alive = false; };
  }, []);
  const label = state === 'online' ? 'API ulangan' : state === 'demo' ? 'Demo rejim' : 'Tekshirilmoqda';
  return (
    <span className={`apistatus apistatus--${state}`} title={state === 'online' ? 'Backend ulangan, real ma\'lumot' : 'Backend topilmadi — demo ma\'lumot'}>
      <span className="apistatus__dot" />
      <span className="apistatus__label mono">{label}</span>
    </span>
  );
}

export default function Navbar() {
  const { isAuthed, user, logout } = useAuth();
  const navigate = useNavigate();
  const [region, setRegion] = useState('Toshkent');
  const isMaster = user?.role === 'MASTER';
  const isAdmin = user?.role === 'ADMIN';

  return (
    <header className="nav">
      <div className="container nav__inner">
        <Link to="/" className="nav__brand" aria-label="Automaster bosh sahifa">
          <Logo />
        </Link>

        <label className="nav__region" title="Hududni tanlang">
          <MapPin size={16} strokeWidth={2.2} />
          <select
            className="nav__region-select"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            aria-label="Hudud"
          >
            {REGIONS.map((r) => <option key={r}>{r}</option>)}
          </select>
          <ChevronDown size={15} className="nav__region-caret" />
        </label>

        <nav className="nav__links" aria-label="Asosiy">
          {!isMaster && !isAdmin && <NavLink to="/masters" className="nav__link">Ustalar</NavLink>}
          {isAuthed && !isAdmin && (
            <NavLink to="/orders" className="nav__link">
              {isMaster ? 'Buyurtmalar' : 'Buyurtmalarim'}
            </NavLink>
          )}
          {isAdmin && <NavLink to="/admin" className="nav__link">Boshqaruv</NavLink>}
          <a className="nav__link" href="/#qanday">Qanday ishlaydi</a>
        </nav>

        <div className="spacer" />

        <ApiStatus />

        <div className="nav__actions">
          {isAuthed ? (
            <>
              {isAdmin ? (
                <Link to="/admin" className="btn btn--sm nav__cta">
                  <Shield size={16} strokeWidth={2.2} /> Boshqaruv
                </Link>
              ) : isMaster ? (
                <Link to="/orders" className="btn btn--sm nav__cta">
                  <ClipboardList size={16} strokeWidth={2.2} /> Buyurtmalar
                </Link>
              ) : (
                <Link to="/orders/new" className="btn btn--sm nav__cta">
                  <Wrench size={16} strokeWidth={2.2} /> Usta chaqirish
                </Link>
              )}
              <div className="nav__user">
                <span className="nav__avatar"><User size={16} strokeWidth={2.2} /></span>
                <span className="nav__uname">{user?.username}</span>
                <button className="nav__logout" onClick={() => { logout(); navigate('/'); }} aria-label="Chiqish">
                  <LogOut size={16} strokeWidth={2.2} />
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn--ghost btn--sm">Kirish</Link>
              <Link to="/register" className="btn btn--sm">Ro'yxatdan o'tish</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
