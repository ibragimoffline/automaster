
export const MOCK_CATEGORIES = [
  { id: 1, name: 'Dvigatel', icon: 'engine', count: 128 },
  { id: 2, name: 'Xodovoy', icon: 'suspension', count: 96 },
  { id: 3, name: 'Elektrika', icon: 'electric', count: 74 },
  { id: 4, name: 'Konditsioner', icon: 'ac', count: 53 },
  { id: 5, name: 'Tormoz tizimi', icon: 'brake', count: 61 },
  { id: 6, name: 'Diagnostika', icon: 'diagnostic', count: 142 },
  { id: 7, name: 'Kuzov & bo\'yoq', icon: 'body', count: 38 },
  { id: 8, name: 'Shina & balans', icon: 'tire', count: 87 },
];

export const MOCK_MASTERS = [
  {
    id: 1, full_name: 'Sardor Qudratov', experience_years: 12, is_verified: true,
    can_visit_customer: true, average_rating: 4.9, total_reviews: 214,
    bio: 'Yapon avtomobillari bo\'yicha mutaxassis. Lexus, Toyota, Nissan diagnostikasi va dvigatel ta\'miri.',
    distance_km: 1.2,
    workshop: { name: 'Avtomatika Servis', region: 'Toshkent', district: 'Yunusobod', open_time: '09:00', close_time: '20:00' },
    specialties: ['Dvigatel', 'Diagnostika'],
  },
  {
    id: 2, full_name: 'Jasur Toirov', experience_years: 8, is_verified: true,
    can_visit_customer: true, average_rating: 4.8, total_reviews: 156,
    bio: 'Xodovoy va tormoz tizimi. Tezkor xizmat, kafolatli ish.',
    distance_km: 2.4,
    workshop: { name: 'Yo\'l Usta', region: 'Toshkent', district: 'Chilonzor', open_time: '08:00', close_time: '21:00' },
    specialties: ['Xodovoy', 'Tormoz tizimi'],
  },
  {
    id: 3, full_name: 'Bekzod Rahimov', experience_years: 15, is_verified: true,
    can_visit_customer: false, average_rating: 5.0, total_reviews: 89,
    bio: 'Avto-elektrika va konditsioner. Murakkab elektr nosozliklarini topish.',
    distance_km: 3.1,
    workshop: { name: 'Volt Garage', region: 'Toshkent', district: 'Mirzo Ulug\'bek', open_time: '09:00', close_time: '19:00' },
    specialties: ['Elektrika', 'Konditsioner'],
  },
  {
    id: 4, full_name: 'Doniyor Aliyev', experience_years: 6, is_verified: false,
    can_visit_customer: true, average_rating: 4.6, total_reviews: 42,
    bio: 'Shina almashtirish, balanslash va tezkor yo\'l yordami.',
    distance_km: 4.7,
    workshop: { name: 'Shina Point', region: 'Toshkent', district: 'Sergeli', open_time: '07:00', close_time: '22:00' },
    specialties: ['Shina & balans'],
  },
  {
    id: 5, full_name: 'Otabek Yusupov', experience_years: 10, is_verified: true,
    can_visit_customer: false, average_rating: 4.7, total_reviews: 173,
    bio: 'Kuzov tiklash va bo\'yoq. Kichik tirnalishdan to og\'ir avariyagacha.',
    distance_km: 5.9,
    workshop: { name: 'Kuzov Pro', region: 'Toshkent', district: 'Olmazor', open_time: '09:00', close_time: '18:00' },
    specialties: ['Kuzov & bo\'yoq'],
  },
];

export const MOCK_SERVICES = [
  { id: 1, title: 'Dvigatel diagnostikasi (OBD)', category_name: 'Diagnostika', price_from: 50000, price_to: 120000, description: 'Kompyuter orqali to\'liq diagnostika va xatolik kodlarini o\'qish.' },
  { id: 2, title: 'Moy va filtr almashtirish', category_name: 'Dvigatel', price_from: 80000, price_to: 150000, description: 'Moy, moy filtri va havo filtrini almashtirish (material narxisiz).' },
  { id: 3, title: 'Tormoz kolodkalari', category_name: 'Tormoz tizimi', price_from: 100000, price_to: 220000, description: 'Old/orqa kolodkalarni almashtirish va disklarni tekshirish.' },
  { id: 4, title: 'Xodovoy diagnostikasi', category_name: 'Xodovoy', price_from: 60000, price_to: 60000, description: 'Podshipnik, rычag va amortizatorlarni to\'liq tekshirish.' },
];

export const MOCK_REVIEWS = [
  { id: 1, rating: 5, comment: 'Juda tez keldi va muammoni 40 daqiqada hal qildi. Narx adolatli, rahmat!', customer_name: 'Aziz', created_at: '2026-06-26T10:00:00Z' },
  { id: 2, rating: 5, comment: 'Diagnostikani puxta qildi, keraksiz ish taklif qilmadi. Ishonchli usta.', customer_name: 'Malika', created_at: '2026-06-20T10:00:00Z' },
  { id: 3, rating: 4, comment: 'Ish sifatli, lekin biroz kech keldi. Umuman olganda mamnunman.', customer_name: 'Rustam', created_at: '2026-06-12T10:00:00Z' },
];

export const MOCK_ORDERS = [
  {
    id: 1042, status: 'ON_THE_WAY', problem_description: 'Dvigatel ishlaganda g\'alati ovoz chiqyapti, quvvati pasaygan.',
    need_master_visit: true, offered_price: 150000, final_price: null,
    created_at: '2026-06-30T08:30:00Z', customer_address: 'Yunusobod 19-kvartal',
    service_category_name: 'Diagnostika',
    master: { id: 1, full_name: 'Sardor Qudratov', average_rating: 4.9, workshop_name: 'Avtomatika Servis' },
  },
  {
    id: 1039, status: 'COMPLETED', problem_description: 'Old tormozlar g\'ichirlaydi.',
    need_master_visit: false, offered_price: 180000, final_price: 165000,
    created_at: '2026-06-24T12:00:00Z', customer_address: 'Chilonzor 7-kvartal',
    service_category_name: 'Tormoz tizimi',
    master: { id: 2, full_name: 'Jasur Toirov', average_rating: 4.8, workshop_name: 'Yo\'l Usta' },
  },
];

export const isMockMaster = (id) => MOCK_MASTERS.some((m) => String(m.id) === String(id));
export const getMockMaster = (id) => MOCK_MASTERS.find((m) => String(m.id) === String(id));
export const getMockOrder = (id) => MOCK_ORDERS.find((o) => String(o.id) === String(id));
