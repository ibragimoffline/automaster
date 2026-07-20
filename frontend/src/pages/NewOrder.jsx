import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft, ArrowRight, Camera, MapPin, Car, Check, AlertTriangle, ShieldCheck, X, Loader2,
  Wrench, ClipboardList,
} from 'lucide-react';
import { api, ApiError } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../components/Toast';
import { MOCK_CATEGORIES, getMockMaster } from '../lib/mock';
import { soum } from '../lib/format';

const STEPS = ['Muammo', 'Joylashuv', 'Tasdiqlash'];

export default function NewOrder() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { user, verifyPhone } = useAuth();
  const toast = useToast();

  const masterId = params.get('master');
  const [master, setMaster] = useState(() => (masterId ? getMockMaster(masterId) : null));
  const [categories, setCategories] = useState(MOCK_CATEGORIES);

  useEffect(() => {
    api.categories()
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.results;
        if (list?.length) setCategories(list);
      })
      .catch(() => {});
    if (masterId) api.master(masterId).then((m) => m && setMaster(m)).catch(() => {});
  }, [masterId]);

  const [step, setStep] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [needVerify, setNeedVerify] = useState(false);

  const [form, setForm] = useState({
    problem_description: '',
    service_category: '',
    customer_address: '',
    customer_latitude: 41.311081,
    customer_longitude: 69.240562,
    need_master_visit: !!master?.can_visit_customer,
    offered_price: '',
  });
  const [photos, setPhotos] = useState([]);
  const [errs, setErrs] = useState({});

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const useMyLocation = () => {
    if (!navigator.geolocation) { toast.error('Brauzer joylashuvni qo\'llab-quvvatlamaydi'); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        set('customer_latitude', +pos.coords.latitude.toFixed(6));
        set('customer_longitude', +pos.coords.longitude.toFixed(6));
        toast.success('Joylashuv aniqlandi');
      },
      () => toast.error('Joylashuvni aniqlab bo\'lmadi — manzilni qo\'lda kiriting'),
    );
  };

  const onPhotos = (e) => {
    const files = [...e.target.files].slice(0, 4 - photos.length);
    const next = files.map((f) => ({ name: f.name, url: URL.createObjectURL(f) }));
    setPhotos((p) => [...p, ...next]);
  };

  const validateStep = () => {
    const e = {};
    if (step === 0) {
      if (form.problem_description.trim().length < 10) e.problem_description = 'Kamida 10 ta belgi — muammoni batafsilroq yozing.';
      if (!form.service_category) e.service_category = 'Xizmat turini tanlang.';
    }
    if (step === 1) {
      if (!form.customer_address.trim()) e.customer_address = 'Manzilni kiriting.';
    }
    setErrs(e);
    return Object.keys(e).length === 0;
  };

  const next = () => { if (validateStep()) setStep((s) => Math.min(s + 1, 2)); };
  const back = () => setStep((s) => Math.max(s - 1, 0));

  const submit = async () => {
    setSubmitting(true);
    setNeedVerify(false);
    try {
      const payload = {
        problem_description: form.problem_description,
        service_category: form.service_category || null,
        master: masterId || null,
        customer_address: form.customer_address,
        customer_latitude: form.customer_latitude,
        customer_longitude: form.customer_longitude,
        need_master_visit: form.need_master_visit,
        offered_price: form.offered_price || null,
      };
      const order = await api.createOrder(payload);
      toast.success('Buyurtma yuborildi!');
      navigate(`/orders/${order.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403 && /telefon/i.test(err.message)) {
        setNeedVerify(true);
      } else {
        toast.error(err.message || 'Buyurtma yuborilmadi');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const doVerify = async () => {
    try { await verifyPhone(); toast.success('Telefon tasdiqlandi'); setNeedVerify(false); submit(); }
    catch { toast.error('Tasdiqlashda xatolik'); }
  };

  const catName = categories.find((c) => String(c.id) === String(form.service_category))?.name;

  if (user?.role === 'MASTER') {
    return (
      <div className="container neworder">
        <div className="empty">
          <span className="empty__icon"><Wrench size={26} /></span>
          <strong>Bu bo'lim mijozlar uchun</strong>
          <span>Usta sifatida siz buyurtma bera olmaysiz — sizga kelgan buyurtmalarni ko'ring va qabul qiling.</span>
          <button className="btn" onClick={() => navigate('/orders')}>
            <ClipboardList size={16} /> Kelgan buyurtmalar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container neworder">
      <button className="backlink" onClick={() => navigate(-1)}><ArrowLeft size={16} /> Orqaga</button>

      <div className="neworder__head">
        <h1 className="neworder__title">Usta chaqirish</h1>
        {master && (
          <span className="neworder__master">
            <Car size={15} /> {master.full_name} · {master.workshop?.name}
          </span>
        )}
      </div>

      <ol className="steps" aria-label="Bosqichlar">
        {STEPS.map((s, i) => (
          <li key={s} className={`steps__item ${i === step ? 'is-active' : ''} ${i < step ? 'is-done' : ''}`}>
            <span className="steps__num mono">{i < step ? <Check size={14} strokeWidth={3} /> : i + 1}</span>
            <span className="steps__label">{s}</span>
          </li>
        ))}
      </ol>

      <div className="neworder__card card">
        {step === 0 && (
          <div className="stack neworder__step">
            <div className={`field ${errs.problem_description ? 'field--err' : ''}`}>
              <label htmlFor="prob">Muammo nima? <span className="req">*</span></label>
              <textarea
                id="prob" className="textarea"
                placeholder="Masalan: dvigatel ishlaganda titroq bor, quvvat tushgan…"
                value={form.problem_description}
                onChange={(e) => set('problem_description', e.target.value)}
              />
              {errs.problem_description ? <span className="err">{errs.problem_description}</span>
                : <span className="hint">Belgilar qancha aniq bo'lsa, usta shuncha tez yordam beradi.</span>}
            </div>

            <div className={`field ${errs.service_category ? 'field--err' : ''}`}>
              <label>Xizmat turi <span className="req">*</span></label>
              <div className="catpick">
                {categories.map((c) => (
                  <button
                    key={c.id} type="button"
                    className={`catpick__opt ${String(form.service_category) === String(c.id) ? 'is-on' : ''}`}
                    onClick={() => set('service_category', c.id)}
                  >{c.name}</button>
                ))}
              </div>
              {errs.service_category && <span className="err">{errs.service_category}</span>}
            </div>

            <div className="field">
              <label>Rasm biriktirish <span className="hint" style={{ fontWeight: 400 }}>(ixtiyoriy, 4 tagacha)</span></label>
              <div className="photos">
                {photos.map((p, i) => (
                  <div key={i} className="photos__item">
                    <img src={p.url} alt={p.name} />
                    <button type="button" className="photos__rm" onClick={() => setPhotos((ps) => ps.filter((_, j) => j !== i))} aria-label="O'chirish"><X size={13} /></button>
                  </div>
                ))}
                {photos.length < 4 && (
                  <label className="photos__add">
                    <Camera size={20} /><span>Qo'shish</span>
                    <input type="file" accept="image/*" multiple hidden onChange={onPhotos} />
                  </label>
                )}
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="stack neworder__step">
            <div className={`field ${errs.customer_address ? 'field--err' : ''}`}>
              <label htmlFor="addr">Manzil <span className="req">*</span></label>
              <input id="addr" className="input" placeholder="Tuman, ko'cha, mo'ljal"
                value={form.customer_address} onChange={(e) => set('customer_address', e.target.value)} />
              {errs.customer_address && <span className="err">{errs.customer_address}</span>}
            </div>

            <button type="button" className="locbtn" onClick={useMyLocation}>
              <span className="locbtn__ic"><MapPin size={18} /></span>
              <span><strong>Joriy joylashuvni aniqlash</strong>
                <span className="mono locbtn__coords">{form.customer_latitude.toFixed(4)}, {form.customer_longitude.toFixed(4)}</span>
              </span>
              <ArrowRight size={16} className="spacer-l" />
            </button>

            <label className={`toggle ${form.need_master_visit ? 'is-on' : ''}`}>
              <span className="toggle__ic"><Car size={20} /></span>
              <span className="toggle__txt">
                <strong>Usta o'zi yetib kelsin</strong>
                <span>Mashina yura olmasa — usta sizning manzilingizga chiqadi.</span>
              </span>
              <span className="toggle__switch" aria-hidden="true"><span /></span>
              <input type="checkbox" className="sr-only" checked={form.need_master_visit}
                onChange={(e) => set('need_master_visit', e.target.checked)} />
            </label>

            <div className="field">
              <label htmlFor="price">Taklif qilingan narx <span className="hint" style={{ fontWeight: 400 }}>(ixtiyoriy, so'm)</span></label>
              <input id="price" className="input mono" inputMode="numeric" placeholder="150000"
                value={form.offered_price} onChange={(e) => set('offered_price', e.target.value.replace(/\D/g, ''))} />
              <span className="hint">Byudjetingizni belgilang — usta rozi bo'lsa qabul qiladi.</span>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="stack neworder__step">
            <h3 className="review__h">Buyurtmani tasdiqlang</h3>
            <dl className="review">
              <div><dt>Muammo</dt><dd>{form.problem_description}</dd></div>
              <div><dt>Xizmat</dt><dd>{catName || '—'}</dd></div>
              {master && <div><dt>Usta</dt><dd>{master.full_name}</dd></div>}
              <div><dt>Manzil</dt><dd>{form.customer_address}</dd></div>
              <div><dt>Chiqib kelish</dt><dd>{form.need_master_visit ? 'Ha, manzilimga' : 'Yo\'q, ustaxonaga boraman'}</dd></div>
              <div><dt>Narx taklifi</dt><dd className="mono">{form.offered_price ? soum(form.offered_price) : 'Kelishiladi'}</dd></div>
              {photos.length > 0 && <div><dt>Rasmlar</dt><dd>{photos.length} ta</dd></div>}
            </dl>

            {needVerify && (
              <div className="verifybox">
                <AlertTriangle size={18} />
                <div>
                  <strong>Telefon raqami tasdiqlanmagan</strong>
                  <span>Buyurtma berish uchun raqamingizni tasdiqlang (demo: bir bosishda).</span>
                </div>
                <button className="btn btn--amber btn--sm" onClick={doVerify}><ShieldCheck size={15} /> Tasdiqlash</button>
              </div>
            )}
          </div>
        )}

        <div className="neworder__nav">
          {step > 0 ? <button className="btn btn--ghost" onClick={back}><ArrowLeft size={16} /> Orqaga</button> : <span />}
          {step < 2
            ? <button className="btn" onClick={next}>Davom etish <ArrowRight size={16} /></button>
            : <button className="btn" onClick={submit} disabled={submitting}>
                {submitting ? <><Loader2 size={16} className="spin" /> Yuborilmoqda…</> : <>Buyurtmani yuborish <Check size={16} /></>}
              </button>}
        </div>
      </div>
    </div>
  );
}
