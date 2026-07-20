export default function Logo({ size = 30, light = false }) {
  const ring = light ? 'rgba(255,255,255,.32)' : 'var(--line-2)';
  const ink = light ? '#fff' : 'var(--ink)';
  return (
    <span className={`logo ${light ? 'logo--light' : ''}`}>
      <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <circle cx="16" cy="16" r="14.5" stroke={ring} strokeWidth="1.5" />
        <circle cx="16" cy="16" r="9" stroke={ring} strokeWidth="1.5" />
        <path d="M16 16 L27 9 A13 13 0 0 0 16 3 Z" fill="var(--cobalt)" opacity="0.16" />
        <line x1="16" y1="16" x2="25.5" y2="9.5" stroke="var(--cobalt)" strokeWidth="2.4" strokeLinecap="round" />
        <circle cx="16" cy="16" r="3" fill={ink} />
        <circle cx="16" cy="16" r="1.3" fill="var(--amber)" />
      </svg>
      <span className="logo__word" style={{ color: light ? '#fff' : 'var(--ink)' }}>
        AUTO<span style={{ color: 'var(--cobalt)' }}>MASTER</span>
      </span>
    </span>
  );
}
