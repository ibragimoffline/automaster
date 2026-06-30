import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Loader2, ArrowRight } from 'lucide-react';
import Logo from '../components/Logo';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../components/Toast';

export default function Login() {
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const loc = useLocation();
  const [form, setForm] = useState({ username: '', password: '' });
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await login(form.username, form.password);
      toast.success('Xush kelibsiz!');
      navigate(loc.state?.from || '/orders');
    } catch (err) {
      toast.error(err.status === 401 ? 'Login yoki parol noto\'g\'ri' : (err.message || 'Kirishda xatolik'));
    } finally { setBusy(false); }
  };

  return (
    <div className="auth">
      <div className="auth__panel">
        <Logo light />
        <h1 className="auth__hero">Mashinangizni<br />ishonchli qo'llarga.</h1>
        <p className="auth__herolede">Yaqin atrofdagi tekshirilgan ustalar, shaffof narx va real vaqtli kuzatuv — barchasi bitta hisobda.</p>
        <ul className="auth__points">
          <li>2 400+ tekshirilgan usta</li>
          <li>14 daqiqada o'rtacha javob</li>
          <li>Ishdan oldin narxni biling</li>
        </ul>
      </div>

      <div className="auth__form-wrap">
        <form className="auth__form" onSubmit={submit}>
          <span className="eyebrow">Hisobga kirish</span>
          <h2 className="auth__title">Qaytganingizdan xursandmiz</h2>

          <div className="field">
            <label htmlFor="u">Foydalanuvchi nomi</label>
            <input id="u" className="input" autoComplete="username" value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="p">Parol</label>
            <input id="p" type="password" className="input" autoComplete="current-password" value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          </div>

          <button className="btn btn--lg btn--block" disabled={busy}>
            {busy ? <><Loader2 size={18} className="spin" /> Kirilmoqda…</> : <>Kirish <ArrowRight size={18} /></>}
          </button>

          <p className="auth__switch">Hisobingiz yo'qmi? <Link to="/register">Ro'yxatdan o'ting</Link></p>
        </form>
      </div>
    </div>
  );
}
