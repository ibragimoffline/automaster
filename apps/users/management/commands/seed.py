import random
from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone

from apps.masters.models import MasterProfile, Workshop
from apps.services.models import ServiceCategory, MasterService
from apps.orders.models import Order, CarProblemImage
from apps.reviews.models import Review

User = get_user_model()
PASSWORD = 'parol1234'


TASHKENT = (41.311081, 69.279737)
DISTRICTS = [
    'Yunusobod', 'Chilonzor', 'Mirzo Ulug\'bek', 'Sergeli', 'Olmazor',
    'Yakkasaroy', 'Shayxontohur', 'Uchtepa', 'Bektemir', 'Yashnobod', 'Mirobod',
]

MASTER_NAMES = [
    'Sardor Qudratov', 'Jasur Toirov', 'Bekzod Rahimov', 'Doniyor Aliyev',
    'Otabek Yusupov', 'Akmal Karimov', 'Sherzod To\'rayev', 'Ulug\'bek Nazarov',
    'Farrux Saidov', 'Javohir Ibrohimov', 'Rustam Eshonov', 'Sanjar Mahmudov',
    'Aziz Islomov', 'Bobur Qodirov', 'Dilshod Yo\'ldoshev', 'Komil Hasanov',
    'Murod Sobirov', 'Nodir Tojiboyev', 'Olim Ergashev', 'Qahramon Usmonov',
    'Shavkat Berdiyev', 'Temur Rashidov', 'Umid Xolmatov', 'Vohid Nematov',
    'Zafar Aripov',
]
WORKSHOP_NAMES = [
    'Avtomatika Servis', 'Yo\'l Usta', 'Volt Garage', 'Shina Point', 'Kuzov Pro',
    'Motor Lux', 'Tezkor Servis', 'Diagnostika Markazi', 'Avto Klinika', 'Pit Stop',
    'Master Auto', 'Mexanika+', 'Turbo Servis', 'Avto Lider', 'Garaj 24',
    'Profi Avto', 'Ustaxona No1', 'Avto Hub', 'Dvigatel Servis', 'Xodovoy Center',
    'Elektro Avto', 'Konditsioner Servis', 'Avto Stil', 'Yangi Motor', 'Toza Avto',
]
CUSTOMER_FIRST = [
    'Aziz', 'Malika', 'Rustam', 'Dilnoza', 'Jahongir', 'Nigora', 'Sanjar', 'Madina',
    'Bekzod', 'Kamola', 'Otabek', 'Sevara', 'Davron', 'Gulnora', 'Shoxrux', 'Laylo',
    'Islom', 'Zilola', 'Farrux', 'Ҳilola', 'Bobur', 'Dilfuza', 'Eldor', 'Munisa',
    'Jasur', 'Charos', 'Akbar', 'Feruza', 'Sardor', 'Nilufar',
]

CATEGORIES = [
    ('Dvigatel', 'Dvigatel ta\'miri va texnik xizmati'),
    ('Xodovoy', 'Yurish qismi: amortizator, rychag, podshipnik'),
    ('Tormoz tizimi', 'Tormoz kolodka, disk va suyuqlik'),
    ('Elektrika', 'Avto-elektrika va simlar'),
    ('Konditsioner', 'Konditsioner ta\'miri va to\'ldirish'),
    ('Diagnostika', 'Kompyuter diagnostikasi (OBD)'),
    ('Kuzov & bo\'yoq', 'Kuzov tiklash va bo\'yoq ishlari'),
    ('Shina & balans', 'Shina almashtirish va balanslash'),
    ('Transmissiya', 'Korobka va ssepleniya'),
    ('Moy almashtirish', 'Moy va filtrlarni almashtirish'),
    ('Akkumulyator', 'Akkumulyator tekshirish va almashtirish'),
    ('Faralar', 'Faralarni sozlash va almashtirish'),
    ('Generator / starter', 'Generator va starter ta\'miri'),
    ('Egzoz tizimi', 'Tutun va egzoz quvurlari'),
    ('Oyna / stakan', 'Oyna almashtirish va tonirovka'),
    ('Signalizatsiya', 'Signalizatsiya va markaziy qulf'),
    ('Salon tozalash', 'Kimyoviy tozalash va himmchistka'),
    ('Razval-sxojdeniye', 'G\'ildiraklar geometriyasi'),
    ('Yog\'lash punkti', 'Tezkor moy va yog\'lash xizmati'),
    ('Yo\'l yordami', 'Joyida tezkor yordam va evakuatsiya'),
]

SERVICE_TITLES = {
    'Dvigatel': ['Dvigatel kapital ta\'miri', 'Tasma (remen) almashtirish', 'Forsunka tozalash'],
    'Xodovoy': ['Xodovoy diagnostikasi', 'Amortizator almashtirish', 'Rychag almashtirish'],
    'Tormoz tizimi': ['Tormoz kolodkalari', 'Tormoz disklari', 'Tormoz suyuqligi'],
    'Elektrika': ['Elektr nosozlik diagnostikasi', 'Provodka ta\'miri', 'Datchik almashtirish'],
    'Konditsioner': ['Konditsioner to\'ldirish', 'Kompressor ta\'miri', 'Radiator tozalash'],
    'Diagnostika': ['Dvigatel diagnostikasi (OBD)', 'To\'liq kompyuter diagnostikasi', 'Xatolik kodlarini o\'qish'],
    'Kuzov & bo\'yoq': ['Element bo\'yash', 'Tirnalish tuzatish', 'Polirovka'],
    'Shina & balans': ['Shina almashtirish', 'G\'ildirak balanslash', 'Shina yamash'],
    'Transmissiya': ['Korobka moyi almashtirish', 'Ssepleniya almashtirish', 'Korobka diagnostikasi'],
    'Moy almashtirish': ['Moy va filtr almashtirish', 'Havo filtri', 'Salon filtri'],
}
DEFAULT_TITLES = ['Diagnostika', 'Ta\'mirlash', 'Profilaktika']

BIOS = [
    'Yapon avtomobillari bo\'yicha mutaxassis. Tezkor va kafolatli ish.',
    'Murakkab nosozliklarni aniqlashda tajribali. Halol narx.',
    '15 yillik tajriba. Har bir mijozga individual yondashuv.',
    'Original ehtiyot qismlar bilan ishlayman. Kafolat beraman.',
    'Tezkor yo\'l yordami va joyida ta\'mir. 24/7 aloqada.',
    'Nemis va koreys avtomobillari bo\'yicha ixtisoslashganman.',
    'Diagnostikadan ta\'mirgacha to\'liq xizmat. Shaffof hisob.',
]
PROBLEMS = [
    'Dvigatel ishlaganda g\'alati ovoz chiqyapti, quvvati pasaygan.',
    'Old tormozlar g\'ichirlaydi va педаль qattiq.',
    'Konditsioner sovutmayapti, faqat issiq havo puflaydi.',
    'Mashina yurganda old tomondan taqillagan ovoz keladi.',
    'Akkumulyator tez o\'tirib qolyapti, ertalab yura olmayapti.',
    'Dvigatel chizig\'i (check) yonib turibdi.',
    'Korobka передачa o\'tkazganda silkinadi.',
    'G\'ildiraklar bir tomonga tortyapti, rul titraydi.',
    'Moy almashtirish va umumiy ko\'rik kerak.',
    'Faralar xira yonadi, biri umuman ishlamaydi.',
    'Salon ichida yonilg\'i hidi bor.',
    'Generator zaryad bermayapti shekilli.',
    'Shina yorilди, zaxira qo\'yish va balanslash kerak.',
    'Vibratsiya bor, ayniqsa tezlikda kuchayadi.',
    'Старter aylanmayapti, faqat shiqillaydi.',
]
COMMENTS = [
    'Juda tez keldi va muammoni hal qildi. Narx adolatli, rahmat!',
    'Diagnostikani puxta qildi, keraksiz ish taklif qilmadi. Ishonchli usta.',
    'Ish sifatli, lekin biroz kech keldi. Umuman mamnunman.',
    'Hammasi joyida, kafolat ham berdi. Tavsiya qilaman.',
    'Professional yondashuv. Endi doim shu ustaga murojaat qilaman.',
    'Narxi arzon emas, lekin sifat shunga yarasha.',
    'Yo\'lda qoldim, 20 daqiqada yetib keldi. Rahmat!',
    'Toza ishladi, mashinani top holatda qaytarib berdi.',
    'Muammoni boshqalar topa olmagandi, bu usta topdi.',
    'Aloqaga juda yaqin, hamma narsani tushuntirib berdi.',
    'Tez, sifatli va halol. 5 ball.',
    'Kichik kamchilik bor edi, lekin qayta to\'g\'irlab berdi.',
]
STATUSES = [
    Order.Status.PENDING, Order.Status.ACCEPTED, Order.Status.ON_THE_WAY,
    Order.Status.IN_PROGRESS, Order.Status.COMPLETED, Order.Status.CANCELLED,
]


class Command(BaseCommand):
    help = 'Automaster DB\'sini demo ma\'lumotlar bilan to\'ldiradi (20+ qator/jadval).'

    def add_arguments(self, parser):
        parser.add_argument('--keep', action='store_true', help='Mavjud ma\'lumotni o\'chirmaydi')

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(42)

        if not opts['keep']:
            self.stdout.write('Eski demo ma\'lumotlar tozalanmoqda…')
            Review.objects.all().delete()
            CarProblemImage.objects.all().delete()
            Order.objects.all().delete()
            MasterService.objects.all().delete()
            Workshop.objects.all().delete()
            MasterProfile.objects.all().delete()
            ServiceCategory.objects.all().delete()
            User.objects.filter(role__in=[User.Role.CUSTOMER, User.Role.MASTER]).delete()

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin', password='admin12345', phone='+998900000000',
                role=User.Role.ADMIN, phone_verified=True)
            self.stdout.write('  superuser yaratildi: admin / admin12345')

        categories = [ServiceCategory.objects.create(name=n, description=d) for n, d in CATEGORIES]
        self.stdout.write(self.style.SUCCESS(f'  ServiceCategory: {len(categories)}'))

        customers = []
        for i, fn in enumerate(CUSTOMER_FIRST):
            u = User(username=f'mijoz{i+1}', first_name=fn,
                     phone=f'+99890{1000000 + i:07d}', role=User.Role.CUSTOMER,
                     phone_verified=True)
            u.set_password(PASSWORD)
            customers.append(u)
        User.objects.bulk_create(customers)
        customers = list(User.objects.filter(role=User.Role.CUSTOMER).order_by('id'))
        self.stdout.write(self.style.SUCCESS(f'  Mijoz (User): {len(customers)}'))

        masters = []
        for i, name in enumerate(MASTER_NAMES):
            u = User(username=f'usta{i+1}', first_name=name.split()[0],
                     phone=f'+99893{2000000 + i:07d}', role=User.Role.MASTER,
                     phone_verified=True)
            u.set_password(PASSWORD)
            u.save()

            profile = MasterProfile.objects.create(
                user=u, full_name=name,
                experience_years=rng.randint(2, 20),
                bio=rng.choice(BIOS),
                is_verified=rng.random() > 0.2,
                can_visit_customer=rng.random() > 0.4,
            )
            Workshop.objects.create(
                master=profile, name=WORKSHOP_NAMES[i],
                region='Toshkent', district=rng.choice(DISTRICTS),
                address=f'{rng.choice(DISTRICTS)} t., {rng.randint(1, 40)}-uy',
                latitude=Decimal(str(round(TASHKENT[0] + rng.uniform(-0.09, 0.09), 6))),
                longitude=Decimal(str(round(TASHKENT[1] + rng.uniform(-0.11, 0.11), 6))),
                open_time=time(rng.choice([8, 9]), 0),
                close_time=time(rng.choice([18, 19, 20, 21]), 0),
            )
            for cat in rng.sample(categories, rng.randint(2, 4)):
                titles = SERVICE_TITLES.get(cat.name, DEFAULT_TITLES)
                title = rng.choice(titles)
                pf = rng.randint(5, 25) * 10000
                MasterService.objects.create(
                    master=profile, category=cat, title=title,
                    price_from=Decimal(pf),
                    price_to=Decimal(pf + rng.randint(3, 12) * 10000) if rng.random() > 0.3 else None,
                    description=f'{title} — sifatli va kafolatli bajariladi.',
                )
            masters.append(profile)
        self.stdout.write(self.style.SUCCESS(f'  Usta (User): {len(masters)}'))
        self.stdout.write(self.style.SUCCESS(f'  MasterProfile: {MasterProfile.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Workshop: {Workshop.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  MasterService: {MasterService.objects.count()}'))

        now = timezone.now()
        orders = []
        for i in range(35):
            customer = rng.choice(customers)
            master = rng.choice(masters)
            status = STATUSES[i % len(STATUSES)] if i < 24 else rng.choice(STATUSES)
            visit = rng.random() > 0.5
            offered = rng.randint(5, 30) * 10000
            o = Order.objects.create(
                customer=customer, master=master,
                service_category=rng.choice(categories),
                problem_description=rng.choice(PROBLEMS),
                customer_latitude=Decimal(str(round(TASHKENT[0] + rng.uniform(-0.08, 0.08), 6))),
                customer_longitude=Decimal(str(round(TASHKENT[1] + rng.uniform(-0.1, 0.1), 6))),
                customer_address=f'{rng.choice(DISTRICTS)} t., {rng.randint(1, 30)}-kvartal',
                need_master_visit=visit,
                status=status,
                offered_price=Decimal(offered),
                final_price=Decimal(offered + rng.randint(-3, 5) * 10000) if status == Order.Status.COMPLETED else None,
            )
            Order.objects.filter(pk=o.pk).update(created_at=now - timedelta(days=rng.randint(0, 30), hours=rng.randint(0, 23)))
            orders.append(o)
        self.stdout.write(self.style.SUCCESS(f'  Order: {len(orders)}'))

        img_count = 0
        for o in orders:
            for _ in range(rng.randint(0, 2)):
                CarProblemImage.objects.create(order=o, image=f'problem_images/demo_{o.pk}_{img_count}.jpg')
                img_count += 1
        while img_count < 22:
            o = rng.choice(orders)
            CarProblemImage.objects.create(order=o, image=f'problem_images/demo_extra_{img_count}.jpg')
            img_count += 1
        self.stdout.write(self.style.SUCCESS(f'  CarProblemImage: {img_count}'))

        completed = [o for o in orders if o.status == Order.Status.COMPLETED]
        while len(completed) < 24:
            customer = rng.choice(customers)
            master = rng.choice(masters)
            offered = rng.randint(5, 30) * 10000
            o = Order.objects.create(
                customer=customer, master=master, service_category=rng.choice(categories),
                problem_description=rng.choice(PROBLEMS),
                customer_latitude=Decimal(str(round(TASHKENT[0] + rng.uniform(-0.08, 0.08), 6))),
                customer_longitude=Decimal(str(round(TASHKENT[1] + rng.uniform(-0.1, 0.1), 6))),
                customer_address=f'{rng.choice(DISTRICTS)} t.',
                need_master_visit=rng.random() > 0.5, status=Order.Status.COMPLETED,
                offered_price=Decimal(offered), final_price=Decimal(offered),
            )
            Order.objects.filter(pk=o.pk).update(created_at=now - timedelta(days=rng.randint(1, 40)))
            completed.append(o)
            orders.append(o)

        rev = 0
        for o in completed:
            if o.master is None or o.master.user_id == o.customer_id:
                continue
            if Review.objects.filter(order=o).exists():
                continue
            Review.objects.create(
                customer=o.customer, master=o.master, order=o,
                rating=rng.choices([5, 4, 3], weights=[7, 2, 1])[0],
                comment=rng.choice(COMMENTS),
            )
            rev += 1
        self.stdout.write(self.style.SUCCESS(f'  Order (yakuniy): {Order.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Review: {rev}'))

        for m in MasterProfile.objects.all():
            agg = m.reviews.aggregate(avg=Avg('rating'), n=Count('id'))
            m.average_rating = round(agg['avg'], 2) if agg['avg'] else 0
            m.total_reviews = agg['n']
            m.save(update_fields=['average_rating', 'total_reviews'])

        self.stdout.write(self.style.SUCCESS('\nTayyor! Barcha demo foydalanuvchilar paroli: ' + PASSWORD))
        self.stdout.write('Masalan: mijoz1 / parol1234  yoki  usta1 / parol1234')
