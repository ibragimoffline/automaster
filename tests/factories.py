from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from apps.masters.models import MasterProfile, Workshop
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.services.models import MasterService, ServiceCategory

User = get_user_model()

DEFAULT_PASSWORD = 'StrongPass123'


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'user{n}')
    first_name = 'Ali'
    last_name = 'Valiyev'
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    phone = factory.Sequence(lambda n: f'+9989{n:08d}')
    phone_verified = False
    role = User.Role.CUSTOMER

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.set_password(extracted or DEFAULT_PASSWORD)
        obj.save(update_fields=['password'])


class CustomerFactory(UserFactory):
    role = User.Role.CUSTOMER
    phone_verified = True


class MasterUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f'master{n}')
    role = User.Role.MASTER
    phone_verified = True


class AdminUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f'admin{n}')
    role = User.Role.ADMIN
    phone_verified = True
    is_staff = True


class MasterProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MasterProfile

    user = factory.SubFactory(MasterUserFactory)
    full_name = factory.Sequence(lambda n: f'Usta {n}')
    experience_years = 5
    bio = 'Tajribali avto usta.'
    is_verified = True
    can_visit_customer = False
    average_rating = Decimal('0.00')
    total_reviews = 0


class WorkshopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workshop

    master = factory.SubFactory(MasterProfileFactory)
    name = factory.Sequence(lambda n: f'Servis {n}')
    region = 'Toshkent'
    district = 'Chilonzor'
    address = 'Bunyodkor ko\'chasi 1'
    latitude = Decimal('41.311081')
    longitude = Decimal('69.240562')


class ServiceCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceCategory

    name = factory.Sequence(lambda n: f'Kategoriya {n}')
    description = 'Kategoriya tavsifi'


class MasterServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MasterService

    master = factory.SubFactory(MasterProfileFactory)
    category = factory.SubFactory(ServiceCategoryFactory)
    title = factory.Sequence(lambda n: f'Xizmat {n}')
    price_from = Decimal('100000.00')
    price_to = Decimal('300000.00')
    description = 'Xizmat tavsifi'


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(CustomerFactory)
    master = factory.SubFactory(MasterProfileFactory)
    service_category = factory.SubFactory(ServiceCategoryFactory)
    problem_description = 'Dvigatel ishlamayapti'
    customer_latitude = Decimal('41.300000')
    customer_longitude = Decimal('69.240000')
    customer_address = 'Toshkent, Chilonzor'
    need_master_visit = False
    status = Order.Status.PENDING
    offered_price = Decimal('200000.00')


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    customer = factory.SubFactory(CustomerFactory)
    master = factory.SubFactory(MasterProfileFactory)
    order = factory.SubFactory(OrderFactory)
    rating = 5
    comment = 'Zo\'r usta!'
