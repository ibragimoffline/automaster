import { Link } from 'react-router-dom';
import { BadgeCheck, MapPin, Car, Clock } from 'lucide-react';
import RatingStars from './RatingStars';
import { km } from '../lib/format';

export default function MasterCard({ master: m }) {
  const ws = m.workshop || {};
  const dist = km(m.distance_km);
  return (
    <Link to={`/masters/${m.id}`} className="mcard card">
      <div className="mcard__top">
        <div className="mcard__avatar" aria-hidden="true">
          {m.full_name?.split(' ').map((w) => w[0]).slice(0, 2).join('')}
        </div>
        <div className="mcard__id">
          <div className="mcard__name">
            {m.full_name}
            {m.is_verified && <BadgeCheck size={17} className="mcard__verified" aria-label="Tekshirilgan usta" />}
          </div>
          <div className="mcard__ws">
            <MapPin size={13} strokeWidth={2.2} />
            {ws.name ? `${ws.name} · ${ws.district || ''}` : (ws.district || 'Ustaxona')}
          </div>
        </div>
        {dist && <span className="mcard__dist mono">{dist}</span>}
      </div>

      <p className="mcard__bio">{m.bio || 'Tajribali avto-usta.'}</p>

      <div className="mcard__tags">
        {(m.specialties || []).slice(0, 3).map((s) => (
          <span key={s} className="badge badge--muted">{s}</span>
        ))}
      </div>

      <div className="mcard__foot">
        <RatingStars value={m.average_rating} count={m.total_reviews} size={14} />
        <div className="mcard__badges">
          {m.can_visit_customer && (
            <span className="badge badge--visit"><Car /> Chiqib boradi</span>
          )}
          <span className="badge badge--muted mono">
            <Clock /> {m.experience_years}+ yil
          </span>
        </div>
      </div>
    </Link>
  );
}
