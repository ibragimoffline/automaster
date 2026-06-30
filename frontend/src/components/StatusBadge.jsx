import { STATUS_LABELS, STATUS_TONE } from '../lib/format';

// Holat belgisi — rang + matn (rang yolg'iz ma'no tashimaydi).
export default function StatusBadge({ status }) {
  const tone = STATUS_TONE[status] || 'muted';
  return (
    <span className={`statusbadge statusbadge--${tone}`}>
      <span className="statusbadge__dot" />
      {STATUS_LABELS[status] || status}
    </span>
  );
}
