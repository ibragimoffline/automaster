# Automaster — Frontend

O'zbekiston avto-usta marketplace'i uchun React + Vite frontend. Django REST
backend'ga (`/api/*`) JWT orqali ulanadi.

## Ishga tushirish

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

Backend (Django) `http://127.0.0.1:8000` da ishlayotgan bo'lsin. Vite dev-proxy
`/api` va `/media` so'rovlarini avtomatik backendga uzatadi (`vite.config.js`).
Backend ulanmagan bo'lsa ham UI **demo ma'lumotlari** bilan to'liq ishlaydi.

```bash
npm run build        # dist/ ga production build
npm run preview
```

## Dizayn tizimi — "Diagnostika / asboblar paneli"

| Element | Tanlov | Sabab |
|--------|--------|-------|
| Asosiy rang | Kobalt `#2348F0` | Diagnostika ekrani / ishonch |
| Aksent | Amber `#FFB200` | Avariya/signal chirog'i — holat, reyting |
| Qorong'i | Ink `#0E1726` | Dvigatel bay soyasi |
| Display shrift | **Archivo** (900) | Sanoat/peshtoq belgisi xarakteri |
| Matn shrifti | **IBM Plex Sans** | Muhandislik merosi |
| Ma'lumot shrifti | **IBM Plex Mono** | Narx/km/reyting — asbob o'qishlari |

Tokenlar: [`src/index.css`](src/index.css) · komponent/sahifa uslublari: [`src/styles/app.css`](src/styles/app.css)

**Imzo elementlari:**
- `ServiceTrack` — buyurtma holati asbob-o'lchagich/yo'l sifatida (kobalt to'ldirish + amber puls).
- `RadarLocator` — yaqin atrofdagi ustalar masofa-halqalarida (haversine "nearby" funksiyasiga bog'langan).

## Tuzilma

```
src/
  api/client.js          JWT + fetch klient (access/refresh, auto-refresh)
  auth/AuthContext.jsx   kirish/ro'yxat/telefon tasdiq
  components/            Navbar, BottomNav, Layout, MasterCard,
                         ServiceTrack, RadarLocator, RatingStars, StatusBadge, Toast
  pages/                 Landing, Masters, MasterDetail, NewOrder,
                         Orders, OrderDetail, Login, Register
  lib/                   format.js (so'm/km/sana/holat), mock.js (demo)
```

## Backend ulanishi

Frontend quyidagi real endpoint'lardan foydalanadi (Vite proxy orqali):

| Endpoint | Ishlatadi |
|----------|-----------|
| `POST /api/token/` | Kirish — token'da `role`/`phone_verified` claim'lari bor |
| `POST /api/auth/register/` | Ro'yxatdan o'tish (tokenlar bilan qaytaradi) |
| `GET /api/masters/nearby/?lat&lng&visiting` | Yaqin ustalar (haversine + `distance_km`, `specialties`) |
| `GET /api/masters/<id>/` | Usta profili |
| `GET /api/services/categories/` | Kategoriyalar + `master_count` |
| `GET /api/services/?master=<id>` | Usta xizmatlari |
| `GET /api/reviews/?master=<id>` | Sharhlar (ommaviy o'qish) |
| `GET/POST /api/orders/`, `/api/orders/<id>/` | Buyurtmalar (avtorizatsiya kerak) |

Navbar'dagi **"API ulangan"** yashil indikator backend ulanganini ko'rsatadi; ulanmasa
sahifalar avtomatik **demo ma'lumotlariga** o'tadi (`src/lib/mock.js`) va "demo" belgisi chiqadi.

### DB'ni demo ma'lumot bilan to'ldirish

```bash
python manage.py seed          # har bir jadval uchun 20+ qator
```

Yaratiladi: 20 kategoriya, 25 usta + profil + ustaxona, 30 mijoz, 75 xizmat, ~50 buyurtma
(turli holatlarda), 24 sharh, 40 muammo-rasmi. Barcha demo parol: **`parol1234`**
(masalan `mijoz1` yoki `usta1`). Django admin: `admin / admin12345`.

### Qolgan cheklov

`CarProblemImage` uchun yozish endpoint'i yo'q — buyurtma rasmlari hozircha faqat lokal
preview, serverga yuborilmaydi. Yuklash endpoint'i qo'shilsa `NewOrder` ulanadi.
