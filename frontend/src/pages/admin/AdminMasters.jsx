import { useEffect, useState, useCallback } from 'react';
import { Search, BadgeCheck, Car } from 'lucide-react';
import RatingStars from '../../components/RatingStars';
import { api } from '../../api/client';
import { useToast } from '../../components/Toast';

export default function AdminMasters() {
  const toast = useToast();
  const [masters, setMasters] = useState(null);
  const [verified, setVerified] = useState('');
  const [q, setQ] = useState('');

  const load = useCallback(() => {
    setMasters(null);
    const params = {};
    if (verified) params.verified = verified;
    if (q.trim()) params.search = q.trim();
    api.adminMasters(params)
      .then((d) => setMasters(Array.isArray(d) ? d : d.results || []))
      .catch(() => { setMasters([]); toast.error('Ustalar yuklanmadi'); });
  }, [verified, q, toast]);

  useEffect(() => { load(); }, [verified]);

  const patch = async (m, body, okMsg) => {
    try {
      const updated = await api.adminUpdateMaster(m.id, body);
      setMasters((list) => list.map((x) => (x.id === m.id ? { ...x, ...updated } : x)));
      if (okMsg) toast.success(okMsg);
    } catch (e) { toast.error(e.message || 'O\'zgartirib bo\'lmadi'); }
  };

  return (
    <div className="apage">
      <div className="apage__bar">
        <form className="apage__search" onSubmit={(e) => { e.preventDefault(); load(); }}>
          <Search size={16} />
          <input placeholder="Usta nomi, ustaxona, telefon" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Qidirish" />
        </form>
        <div className="apage__filters">
          <button className={`pill ${verified === '' ? 'is-on' : ''}`} onClick={() => setVerified('')}>Hammasi</button>
          <button className={`pill ${verified === 'true' ? 'is-on' : ''}`} onClick={() => setVerified('true')}>Tekshirilgan</button>
          <button className={`pill ${verified === 'false' ? 'is-on' : ''}`} onClick={() => setVerified('false')}>Kutilmoqda</button>
        </div>
      </div>

      {masters === null ? (
        <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />
      ) : (
        <div className="atable-wrap card">
          <table className="atable">
            <thead>
              <tr>
                <th>Usta</th><th>Ustaxona</th><th>Reyting</th><th className="ta-c">Tajriba</th>
                <th className="ta-c">Tekshirilgan</th><th className="ta-c">Chiqib boradi</th>
              </tr>
            </thead>
            <tbody>
              {masters.map((m) => (
                <tr key={m.id}>
                  <td>
                    <div className="acell-user">
                      <span className="acell-avatar">{m.full_name.split(' ').map((w) => w[0]).slice(0, 2).join('')}</span>
                      <div>
                        <strong>{m.full_name}{m.is_verified && <BadgeCheck size={14} className="acell-verified" />}</strong>
                        <span className="acell-sub mono">{m.phone}</span>
                      </div>
                    </div>
                  </td>
                  <td>{m.workshop_name || '—'}<br /><span className="acell-sub">{m.district || ''}</span></td>
                  <td><RatingStars value={m.average_rating} count={m.total_reviews} size={13} /></td>
                  <td className="ta-c mono">{m.experience_years} yil</td>
                  <td className="ta-c">
                    <button className={`atoggle ${m.is_verified ? 'is-on' : ''}`} title="Tekshiruv"
                      onClick={() => patch(m, { is_verified: !m.is_verified }, m.is_verified ? 'Tekshiruv olib tashlandi' : 'Usta tasdiqlandi')}>
                      <span /></button>
                  </td>
                  <td className="ta-c">
                    <button className={`atoggle ${m.can_visit_customer ? 'is-on' : ''}`} title="Chiqib borish"
                      onClick={() => patch(m, { can_visit_customer: !m.can_visit_customer })}>
                      <span /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {masters.length === 0 && <div className="empty"><strong>Topilmadi</strong></div>}
        </div>
      )}
    </div>
  );
}
