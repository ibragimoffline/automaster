import { useEffect, useState } from 'react';
import { Trash2 } from 'lucide-react';
import RatingStars from '../../components/RatingStars';
import { api } from '../../api/client';
import { useToast } from '../../components/Toast';
import { relTime } from '../../lib/format';

export default function AdminReviews() {
  const toast = useToast();
  const [reviews, setReviews] = useState(null);

  const load = () => api.adminReviews()
    .then((d) => setReviews(Array.isArray(d) ? d : d.results || []))
    .catch(() => { setReviews([]); toast.error('Sharhlar yuklanmadi'); });

  useEffect(() => { load(); }, []); // eslint-disable-line

  const remove = async (r) => {
    if (!window.confirm('Sharhni o\'chirasizmi? Usta reytingi qayta hisoblanadi.')) return;
    try {
      await api.adminDeleteReview(r.id);
      setReviews((list) => list.filter((x) => x.id !== r.id));
      toast.success('Sharh o\'chirildi');
    } catch (e) { toast.error(e.message || 'O\'chirib bo\'lmadi'); }
  };

  if (reviews === null) return <div className="skeleton" style={{ height: 280, borderRadius: 14 }} />;

  return (
    <div className="apage">
      <div className="atable-wrap card">
        <table className="atable">
          <thead><tr><th>Mijoz</th><th>Usta</th><th>Baho</th><th>Izoh</th><th>Sana</th><th></th></tr></thead>
          <tbody>
            {reviews.map((r) => (
              <tr key={r.id}>
                <td>{r.customer_username}</td>
                <td>{r.master_name}</td>
                <td><RatingStars value={r.rating} showValue={false} size={13} /></td>
                <td className="acell-desc">{r.comment || <span className="acell-sub">—</span>}</td>
                <td className="mono acell-sub">{relTime(r.created_at)}</td>
                <td className="ta-r">
                  <button className="aicon-btn aicon-btn--danger" title="O'chirish" onClick={() => remove(r)}><Trash2 size={16} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {reviews.length === 0 && <div className="empty"><strong>Sharh yo'q</strong></div>}
      </div>
    </div>
  );
}
