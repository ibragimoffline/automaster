import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Loader2, ArrowRight, User, Wrench } from 'lucide-react';
import Logo from '../components/Logo';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../components/Toast';

export default function Register() {
  const { register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    role: 'CUSTOMER', first_name: '', username: '', phone: '', password: '',
  });
  const [busy, setBusy] = useState(false);
  const [errs, setErrs] = useState({});

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    const er = {};
    if (form.password.length < 8) er.password = 'Parol kamida 8 ta belgidan iborat bo\'lsin.';
    if (!/^\+?\d{9,15}$/.test(form.phone.replace(/\s/g, ''))) er.phone = 'Telefon raqamini to\'g\'ri kiriting.';
    setErrs(er);
    if (Object.keys(er).length) return;

    setBusy(true);
    try {
      await register({
        username: form.username,
        first_name: form.first_name,
        phone: form.phone.replace(/\s/g, ''),
        password: form.password,
        role: form.role,
      });
      toast.success('Hisob yaratildi!');
      navigate(form.role === 'MASTER' ? '/' : '/orders/new');
    } catch (err) {
      toast.error(err.message || 'Ro\'yxatdan o\'tishda xatolik');
      if (err.data) setErrs(err.data);
    } finally { setBusy(false); }
  };

  return (
    <div className="auth">
      <div className="auth__panel auth__panel--amber">
        <Logo light />
        <h1 className="auth__hero">Bir necha daqiqada<br />ishga tushing.</h1>
        <p className="auth__herolede">Mijoz sifatida usta chaqiring yoki usta sifatida yangi buyurtmalar oling.</p>
        <ul className="auth__points">
          <li>Bepul ro'yxatdan o'tish</li>
          <li>Telefon orqali tasdiq</li>
          <li>Xavfsiz to'lov tizimi</li>
        </ul>
      </div>

      <div className="auth__form-wrap">
        <form className="auth__form" onSubmit={submit}>
          <span className="eyebrow">Yangi hisob</span>
          <h2 className="auth__title">Automaster'ga qo'shiling</h2>

          <div className="rolepick" role="radiogroup" aria-label="Hisob turi">
            <button type="button" role="radio" aria-checked={form.role === 'CUSTOMER'}
              className={`rolepick__opt ${form.role === 'CUSTOMER' ? 'is-on' : ''}`} onClick={() => set('role', 'CUSTOMER')}>
              <User size={20} /><strong>Mijozman</strong><span>Usta qidiraman</span>
            </button>
            <button type="button" role="radio" aria-checked={form.role === 'MASTER'}
              className={`rolepick__opt ${form.role === 'MASTER' ? 'is-on' : ''}`} onClick={() => set('role', 'MASTER')}>
              <Wrench size={20} /><strong>Ustaman</strong><span>Buyurtma olaman</span>
            </button>
          </div>

          <div className="field">
            <label htmlFor="fn">Ism</label>
            <input id="fn" className="input" value={form.first_name} onChange={(e) => set('first_name', e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="ru">Foydalanuvchi nomi</label>
            <input id="ru" className="input" autoComplete="username" value={form.username} onChange={(e) => set('username', e.target.value)} required />
          </div>
          <div className={`field ${errs.phone ? 'field--err' : ''}`}>
            <label htmlFor="ph">Telefon</label>
            <input id="ph" type="tel" className="input mono" inputMode="tel" placeholder="+998 90 123 45 67"
              value={form.phone} onChange={(e) => set('phone', e.target.value)} required />
            {errs.phone && <span className="err">{Array.isArray(errs.phone) ? errs.phone[0] : errs.phone}</span>}
          </div>
          <div className={`field ${errs.password ? 'field--err' : ''}`}>
            <label htmlFor="rp">Parol</label>
            <input id="rp" type="password" className="input" autoComplete="new-password" value={form.password} onChange={(e) => set('password', e.target.value)} required />
            {errs.password ? <span className="err">{Array.isArray(errs.password) ? errs.password[0] : errs.password}</span>
              : <span className="hint">Kamida 8 ta belgi.</span>}
          </div>

          <button className="btn btn--lg btn--block" disabled={busy}>
            {busy ? <><Loader2 size={18} className="spin" /> Yaratilmoqda…</> : <>Hisob yaratish <ArrowRight size={18} /></>}
          </button>

          <p className="auth__switch">Hisobingiz bormi? <Link to="/login">Kiring</Link></p>
        </form>
      </div>
    </div>
  );
}
