import { Outlet, Link } from 'react-router-dom';
import Navbar from './Navbar';
import BottomNav from './BottomNav';
import Logo from './Logo';

export default function Layout() {
  return (
    <>
      <a href="#main" className="skip-link">Asosiy qismga o'tish</a>
      <Navbar />
      <main id="main" className="app-main">
        <Outlet />
      </main>
      <Footer />
      <BottomNav />
    </>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div className="footer__brand">
          <Logo light />
          <p className="footer__tag">Yaqin atrofdagi ishonchli avto-ustani daqiqalar ichida toping.</p>
        </div>
        <div className="footer__cols">
          <div>
            <h4 className="footer__h">Xizmat</h4>
            <Link to="/masters">Ustalar</Link>
            <Link to="/orders/new">Usta chaqirish</Link>
            <a href="/#qanday">Qanday ishlaydi</a>
          </div>
          <div>
            <h4 className="footer__h">Ustalar uchun</h4>
            <Link to="/register">Usta bo'lish</Link>
            <a href="/#trust">Tekshiruv</a>
            <a href="/#qanday">To'lov</a>
          </div>
          <div>
            <h4 className="footer__h">Aloqa</h4>
            <a href="tel:+998711234567">+998 71 123 45 67</a>
            <a href="mailto:salom@automaster.uz">salom@automaster.uz</a>
            <span className="mono footer__city">Toshkent · 09:00–22:00</span>
          </div>
        </div>
      </div>
      <div className="container footer__base">
        <span className="mono">© 2026 AUTOMASTER</span>
        <span className="mono footer__base-r">O'zbekiston · avto-usta platformasi</span>
      </div>
    </footer>
  );
}
