import { Check, Send, ShieldCheck, Navigation, Wrench, Flag } from 'lucide-react';
import { STATUS_FLOW, STATUS_LABELS } from '../lib/format';

const ICONS = {
  PENDING: Send, ACCEPTED: ShieldCheck, ON_THE_WAY: Navigation,
  IN_PROGRESS: Wrench, COMPLETED: Flag,
};
const SUBLABEL = {
  PENDING: 'soʻrov yuborildi',
  ACCEPTED: 'usta tasdiqladi',
  ON_THE_WAY: 'usta yetib kelmoqda',
  IN_PROGRESS: 'taʼmir boshlandi',
  COMPLETED: 'ish topshirildi',
};

export default function ServiceTrack({ status, terminal }) {
  const isTerminalBad = status === 'CANCELLED' || status === 'REJECTED';
  const activeIndex = isTerminalBad ? -1 : STATUS_FLOW.indexOf(status);
  const fillPct = activeIndex <= 0 ? 0 : (activeIndex / (STATUS_FLOW.length - 1)) * 100;

  return (
    <div className="track" role="list" aria-label="Buyurtma holati">
      <div className="track__rail">
        <div className="track__fill" style={{ '--fill': `${fillPct}%` }} />
      </div>
      <ol className="track__stations">
        {STATUS_FLOW.map((s, i) => {
          const Icon = ICONS[s];
          const done = activeIndex > i;
          const active = activeIndex === i;
          const state = done ? 'done' : active ? 'active' : 'todo';
          return (
            <li key={s} className={`station station--${state}`} role="listitem">
              <span className="station__node" aria-hidden="true">
                {active && <span className="station__pulse" />}
                {done ? <Check size={16} strokeWidth={3} /> : <Icon size={16} strokeWidth={2.3} />}
              </span>
              <span className="station__label">{STATUS_LABELS[s]}</span>
              <span className="station__sub mono">{active ? SUBLABEL[s] : ''}</span>
            </li>
          );
        })}
      </ol>
      {isTerminalBad && (
        <div className="track__terminal">{STATUS_LABELS[status]}</div>
      )}
    </div>
  );
}
