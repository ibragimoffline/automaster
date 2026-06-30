import { useMemo } from 'react';
import { MapPin } from 'lucide-react';

// ——— Lokator paneli ———
// Haqiqiy xarita o'rniga mavzuga mos radar: yaqin atrofdagi ustalarni masofa
// halqalarida ko'rsatadi (haversine "nearby" backend funksiyasiga bog'langan).
// Pinlar masofa bo'yicha radiusda, indeks bo'yicha burchakda joylashtiriladi.
export default function RadarLocator({ masters = [], activeId, onPick, sweep = true, compact = false }) {
  const maxKm = useMemo(
    () => Math.max(5, ...masters.map((m) => m.distance_km || 0)),
    [masters]
  );

  const pins = masters.slice(0, 8).map((m, i) => {
    const r = 0.16 + 0.78 * Math.min(1, (m.distance_km || (i + 1)) / maxKm);
    // Indeks bo'yicha tarqatilgan burchak (oltin burchak — yopishib qolmasligi uchun)
    const angle = (i * 137.5 - 90) * (Math.PI / 180);
    const cx = 50 + Math.cos(angle) * r * 42;
    const cy = 50 + Math.sin(angle) * r * 42;
    return { m, cx, cy };
  });

  return (
    <div className={`radar ${compact ? 'radar--compact' : ''}`} aria-hidden={compact ? 'true' : undefined}>
      <svg viewBox="0 0 100 100" className="radar__svg">
        <defs>
          <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#2348F0" stopOpacity="0.10" />
            <stop offset="70%" stopColor="#2348F0" stopOpacity="0.02" />
            <stop offset="100%" stopColor="#2348F0" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="50" cy="50" r="48" fill="url(#radarGlow)" />
        {[16, 30, 44].map((r) => (
          <circle key={r} cx="50" cy="50" r={r} fill="none" stroke="var(--line)" strokeWidth="0.5" strokeDasharray="1.5 2" />
        ))}
        <line x1="50" y1="2" x2="50" y2="98" stroke="var(--line)" strokeWidth="0.4" />
        <line x1="2" y1="50" x2="98" y2="50" stroke="var(--line)" strokeWidth="0.4" />
        {sweep && (
          <g className="radar__sweep" style={{ transformOrigin: '50px 50px' }}>
            <path d="M50 50 L50 4 A46 46 0 0 1 92 38 Z" fill="#2348F0" opacity="0.08" />
          </g>
        )}
        {/* foydalanuvchi markazi */}
        <circle cx="50" cy="50" r="3.2" fill="var(--cobalt)" />
        <circle cx="50" cy="50" r="3.2" fill="none" stroke="var(--cobalt)" strokeWidth="0.6" className="radar__ping" />
      </svg>

      {pins.map(({ m, cx, cy }) => (
        <button
          key={m.id}
          className={`radar__pin ${activeId === m.id ? 'is-active' : ''} ${m.is_verified ? 'is-verified' : ''}`}
          style={{ left: `${cx}%`, top: `${cy}%` }}
          onClick={() => onPick?.(m)}
          tabIndex={compact ? -1 : 0}
          aria-label={`${m.full_name}, ${m.distance_km ? m.distance_km.toFixed(1) + ' km' : ''}`}
        >
          <MapPin size={compact ? 13 : 16} fill="currentColor" strokeWidth={1.5} />
          {!compact && <span className="radar__pin-label">{m.full_name?.split(' ')[0]}</span>}
        </button>
      ))}

      <span className="radar__center-label mono">SIZ</span>
    </div>
  );
}
