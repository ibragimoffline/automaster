import { Star } from 'lucide-react';

export default function RatingStars({ value = 0, count, size = 15, showValue = true, interactive = false, onRate }) {
  const v = Number(value) || 0;
  return (
    <span className={`stars ${interactive ? 'stars--interactive' : ''}`}>
      <span className="stars__row" role={interactive ? 'radiogroup' : undefined} aria-label={`Reyting ${v} / 5`}>
        {[1, 2, 3, 4, 5].map((i) => {
          const filled = i <= Math.round(v);
          const star = (
            <Star
              size={size}
              strokeWidth={2}
              className={filled ? 'star is-filled' : 'star'}
              fill={filled ? 'var(--amber)' : 'none'}
            />
          );
          return interactive ? (
            <button
              key={i}
              type="button"
              className="stars__btn"
              onClick={() => onRate?.(i)}
              aria-label={`${i} yulduz`}
              role="radio"
              aria-checked={i === Math.round(v)}
            >{star}</button>
          ) : <span key={i}>{star}</span>;
        })}
      </span>
      {showValue && (
        <span className="stars__meta mono">
          {v > 0 ? v.toFixed(1) : '—'}{count != null && <span className="stars__count"> · {count}</span>}
        </span>
      )}
    </span>
  );
}
