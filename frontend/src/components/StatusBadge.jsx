import { STATUS_LABELS, STATUS_TONE } from '../lib/format';

export default function StatusBadge({ status }) {
  const tone = STATUS_TONE[status] || 'muted';
  return (
    <span className={`statusbadge statusbadge--${tone}`}>
      <span className="statusbadge__dot" />
      {STATUS_LABELS[status] || status}
    </span>
  );
}
