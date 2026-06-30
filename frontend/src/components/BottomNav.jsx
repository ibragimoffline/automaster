import { NavLink } from 'react-router-dom';
import { Home, Search, PlusCircle, ClipboardList, User, History, Inbox } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

// Mobil pastki navigatsiya — rolega qarab (maks 5 element).
export default function BottomNav() {
  const { isAuthed, user } = useAuth();
  const isMaster = user?.role === 'MASTER';

  const items = isMaster
    ? [
        { to: '/', icon: Home, label: 'Bosh', end: true },
        { to: '/masters', icon: Search, label: 'Ustalar' },
        { to: '/orders', icon: Inbox, label: 'Buyurtma', primary: true, end: true },
        { to: '/orders?tab=history', icon: History, label: 'Tarix' },
        { to: '/orders', icon: User, label: 'Profil' },
      ]
    : [
        { to: '/', icon: Home, label: 'Bosh', end: true },
        { to: '/masters', icon: Search, label: 'Ustalar' },
        { to: '/orders/new', icon: PlusCircle, label: 'Chaqirish', primary: true },
        { to: isAuthed ? '/orders' : '/login', icon: ClipboardList, label: 'Buyurtma' },
        { to: isAuthed ? '/orders' : '/login', icon: User, label: isAuthed ? 'Profil' : 'Kirish' },
      ];

  return (
    <nav className="bottomnav" aria-label="Mobil navigatsiya">
      {items.map(({ to, icon: Icon, label, primary, end }) => (
        <NavLink
          key={label}
          to={to}
          end={end}
          className={({ isActive }) =>
            `bottomnav__item ${isActive ? 'is-active' : ''} ${primary ? 'bottomnav__item--primary' : ''}`}
        >
          <Icon size={primary ? 26 : 22} strokeWidth={2.1} />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
