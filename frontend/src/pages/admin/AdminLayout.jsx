import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Wrench, ClipboardList, Tag, Star, Shield } from 'lucide-react';

const TABS = [
  { to: '/admin', end: true, icon: LayoutDashboard, label: 'Panel' },
  { to: '/admin/users', icon: Users, label: 'Foydalanuvchilar' },
  { to: '/admin/masters', icon: Wrench, label: 'Ustalar' },
  { to: '/admin/orders', icon: ClipboardList, label: 'Buyurtmalar' },
  { to: '/admin/categories', icon: Tag, label: 'Kategoriyalar' },
  { to: '/admin/reviews', icon: Star, label: 'Sharhlar' },
];

export default function AdminLayout() {
  return (
    <div className="container admin">
      <div className="admin__head">
        <span className="admin__badge"><Shield size={15} /> ADMIN</span>
        <h1 className="admin__title">Boshqaruv paneli</h1>
      </div>
      <div className="admin__shell">
        <nav className="admin__nav" aria-label="Boshqaruv bo'limlari">
          {TABS.map(({ to, end, icon: Icon, label }) => (
            <NavLink key={to} to={to} end={end}
              className={({ isActive }) => `admin__navlink ${isActive ? 'is-on' : ''}`}>
              <Icon size={18} strokeWidth={2.1} /> <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="admin__content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
