from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.orders.models import CarProblemImage, Order
from tests.base import BaseAPITestCase
from tests.factories import (
    AdminUserFactory,
    CustomerFactory,
    MasterProfileFactory,
    MasterUserFactory,
    OrderFactory,
    ServiceCategoryFactory,
)

LIST_URL = reverse('order-list')


def detail_url(pk):
    return reverse('order-detail', args=[pk])


def accept_url(pk):
    return reverse('order-accept', args=[pk])


def complete_url(pk):
    return reverse('order-complete', args=[pk])


class OrderCreateAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.master = MasterProfileFactory()
        self.category = ServiceCategoryFactory()

    def payload(self, **overrides):
        data = {
            'master': self.master.id,
            'service_category': self.category.id,
            'problem_description': 'Tormoz ishlamayapti',
            'customer_latitude': '41.311081',
            'customer_longitude': '69.240562',
            'customer_address': 'Toshkent, Chilonzor 5',
            'need_master_visit': True,
            'offered_price': '250000.00',
        }
        data.update(overrides)
        return data

    def test_anonymous_cannot_create_order(self):
        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_verified_customer_creates_order(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.master, self.master)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertTrue(order.need_master_visit)

    def test_customer_is_forced_to_request_user(self):
        other = CustomerFactory()
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(customer=other.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.get().customer, self.customer)

    def test_status_is_forced_to_pending(self):
        self.auth(self.customer)

        resp = self.client.post(
            LIST_URL, self.payload(status=Order.Status.COMPLETED), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.get().status, Order.Status.PENDING)

    def test_final_price_is_read_only_on_create(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(final_price='999999.00'), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Order.objects.get().final_price)

    def test_unverified_customer_cannot_create_order(self):
        self.auth(CustomerFactory(phone_verified=False))

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_master_cannot_create_order(self):
        self.auth(MasterUserFactory())

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_admin_cannot_create_order(self):
        self.auth(AdminUserFactory())

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_problem_description_rejected(self):
        self.auth(self.customer)

        resp = self.client.post(
            LIST_URL, self.payload(problem_description=''), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('problem_description', resp.data)

    def test_missing_coordinates_rejected(self):
        self.auth(self.customer)
        data = self.payload()
        del data['customer_latitude']

        resp = self.client.post(LIST_URL, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_latitude', resp.data)

    def test_order_without_master_is_allowed(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(master=None), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(Order.objects.get().master)


class OrderListAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.other_customer = CustomerFactory()
        self.master = MasterProfileFactory()
        self.other_master = MasterProfileFactory()

        self.my_order = OrderFactory(customer=self.customer, master=self.master)
        self.other_order = OrderFactory(customer=self.other_customer, master=self.other_master)

    def test_anonymous_cannot_list(self):
        resp = self.client.get(LIST_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_only_own_orders(self):
        self.auth(self.customer)

        resp = self.client.get(LIST_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual([o['id'] for o in resp.data], [self.my_order.id])

    def test_master_sees_only_orders_assigned_to_them(self):
        self.auth(self.master.user)

        resp = self.client.get(LIST_URL)

        self.assertEqual([o['id'] for o in resp.data], [self.my_order.id])

    def test_admin_sees_only_their_own_customer_orders(self):
        admin = AdminUserFactory()
        admin_order = OrderFactory(customer=admin)
        self.auth(admin)

        resp = self.client.get(LIST_URL)

        self.assertEqual([o['id'] for o in resp.data], [admin_order.id])

    def test_customer_cannot_retrieve_someone_elses_order(self):
        self.auth(self.customer)

        resp = self.client.get(detail_url(self.other_order.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_can_retrieve_own_order(self):
        self.auth(self.customer)

        resp = self.client.get(detail_url(self.my_order.id))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.my_order.id)

    def test_filter_by_status(self):
        OrderFactory(customer=self.customer, status=Order.Status.COMPLETED)
        self.auth(self.customer)

        resp = self.client.get(LIST_URL, {'status': Order.Status.COMPLETED})

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['status'], Order.Status.COMPLETED)

    def test_filter_by_need_master_visit(self):
        visit_order = OrderFactory(customer=self.customer, need_master_visit=True)
        self.auth(self.customer)

        resp = self.client.get(LIST_URL, {'need_master_visit': 'true'})

        self.assertEqual([o['id'] for o in resp.data], [visit_order.id])

    def test_payload_contains_denormalised_names(self):
        self.auth(self.customer)

        resp = self.client.get(detail_url(self.my_order.id))

        self.assertEqual(resp.data['customer_username'], self.customer.username)
        self.assertEqual(resp.data['master_name'], self.master.full_name)
        self.assertEqual(resp.data['service_category_name'], self.my_order.service_category.name)

    def test_images_are_included(self):
        CarProblemImage.objects.create(order=self.my_order, image='problem_images/x.jpg')
        self.auth(self.customer)

        resp = self.client.get(detail_url(self.my_order.id))

        self.assertEqual(len(resp.data['images']), 1)


class OrderAcceptAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.master = MasterProfileFactory()
        self.order = OrderFactory(
            customer=self.customer, master=self.master, status=Order.Status.PENDING)

    def test_assigned_master_accepts_pending_order(self):
        self.auth(self.master.user)

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], Order.Status.ACCEPTED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.ACCEPTED)

    def test_customer_cannot_accept_own_order(self):
        self.auth(self.customer)

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)

    def test_other_master_gets_404(self):
        self.auth(MasterProfileFactory().user)

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_accept(self):
        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_accept_twice(self):
        self.auth(self.master.user)
        self.client.post(accept_url(self.order.id))

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_completed_order(self):
        self.order.status = Order.Status.COMPLETED
        self.order.save(update_fields=['status'])
        self.auth(self.master.user)

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_accept_cancelled_order(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save(update_fields=['status'])
        self.auth(self.master.user)

        resp = self.client.post(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_requires_post(self):
        self.auth(self.master.user)

        resp = self.client.get(accept_url(self.order.id))

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderCompleteAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.master = MasterProfileFactory()
        self.order = OrderFactory(
            customer=self.customer, master=self.master, status=Order.Status.ACCEPTED)

    def test_assigned_master_completes_order_with_final_price(self):
        self.auth(self.master.user)

        resp = self.client.post(
            complete_url(self.order.id), {'final_price': '350000.00'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], Order.Status.COMPLETED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.final_price, Decimal('350000.00'))

    def test_complete_without_final_price_keeps_it_null(self):
        self.auth(self.master.user)

        resp = self.client.post(complete_url(self.order.id), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.COMPLETED)
        self.assertIsNone(self.order.final_price)

    def test_customer_cannot_complete_order(self):
        self.auth(self.customer)

        resp = self.client.post(complete_url(self.order.id), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.ACCEPTED)

    def test_other_master_gets_404(self):
        self.auth(MasterProfileFactory().user)

        resp = self.client.post(complete_url(self.order.id), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_complete(self):
        resp = self.client.post(complete_url(self.order.id), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_from_pending_skips_accept(self):
        pending = OrderFactory(
            customer=self.customer, master=self.master, status=Order.Status.PENDING)
        self.auth(self.master.user)

        resp = self.client.post(complete_url(pending.id), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        pending.refresh_from_db()
        self.assertEqual(pending.status, Order.Status.COMPLETED)


class OrderContactUnlockAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory(phone='+998901110001')
        self.master = MasterProfileFactory()
        self.master.user.phone = '+998902220002'
        self.master.user.save(update_fields=['phone'])

    def make_order(self, status_value):
        return OrderFactory(customer=self.customer, master=self.master, status=status_value)

    def test_pending_order_is_locked(self):
        order = self.make_order(Order.Status.PENDING)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertFalse(resp.data['contact_unlocked'])

    def test_customer_cannot_see_master_phone_while_pending(self):
        order = self.make_order(Order.Status.PENDING)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertIsNone(resp.data['master_phone'])

    def test_customer_sees_master_phone_after_accept(self):
        order = self.make_order(Order.Status.ACCEPTED)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertTrue(resp.data['contact_unlocked'])
        self.assertEqual(resp.data['master_phone'], '+998902220002')

    def test_customer_always_sees_own_phone(self):
        order = self.make_order(Order.Status.PENDING)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertEqual(resp.data['customer_phone'], '+998901110001')

    def test_master_cannot_see_customer_phone_while_pending(self):
        order = self.make_order(Order.Status.PENDING)
        self.auth(self.master.user)

        resp = self.client.get(detail_url(order.id))

        self.assertIsNone(resp.data['customer_phone'])

    def test_master_sees_customer_phone_after_accept(self):
        order = self.make_order(Order.Status.ACCEPTED)
        self.auth(self.master.user)

        resp = self.client.get(detail_url(order.id))

        self.assertEqual(resp.data['customer_phone'], '+998901110001')

    def test_master_always_sees_own_phone(self):
        order = self.make_order(Order.Status.PENDING)
        self.auth(self.master.user)

        resp = self.client.get(detail_url(order.id))

        self.assertEqual(resp.data['master_phone'], '+998902220002')

    def test_cancelled_order_relocks_contacts(self):
        order = self.make_order(Order.Status.CANCELLED)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertFalse(resp.data['contact_unlocked'])
        self.assertIsNone(resp.data['master_phone'])

    def test_order_without_master_has_no_master_phone(self):
        order = OrderFactory(
            customer=self.customer, master=None, status=Order.Status.ACCEPTED)
        self.auth(self.customer)

        resp = self.client.get(detail_url(order.id))

        self.assertIsNone(resp.data['master_phone'])



@pytest.mark.django_db
@pytest.mark.parametrize(
    'order_status,unlocked',
    [
        (Order.Status.PENDING, False),
        (Order.Status.ACCEPTED, True),
        (Order.Status.ON_THE_WAY, True),
        (Order.Status.IN_PROGRESS, True),
        (Order.Status.COMPLETED, True),
        (Order.Status.CANCELLED, False),
        (Order.Status.REJECTED, False),
    ],
)
def test_contact_unlocked_per_status(auth_client, order_status, unlocked):
    customer = CustomerFactory()
    order = OrderFactory(customer=customer, status=order_status)

    resp = auth_client(customer).get(detail_url(order.id))

    assert resp.data['contact_unlocked'] is unlocked


@pytest.mark.django_db
def test_order_str():
    order = OrderFactory(status=Order.Status.PENDING)

    assert str(order) == f'Order #{order.id} - PENDING'


@pytest.mark.django_db
def test_deleting_master_keeps_order_and_nulls_master():
    order = OrderFactory()

    order.master.delete()
    order.refresh_from_db()

    assert Order.objects.filter(id=order.id).exists()
    assert order.master is None


@pytest.mark.django_db
def test_deleting_customer_cascades_to_order():
    order = OrderFactory()

    order.customer.delete()

    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_deleting_order_cascades_to_images():
    order = OrderFactory()
    CarProblemImage.objects.create(order=order, image='problem_images/x.jpg')

    order.delete()

    assert CarProblemImage.objects.count() == 0


@pytest.mark.django_db
def test_full_order_lifecycle(auth_client):
    customer = CustomerFactory()
    master = MasterProfileFactory()
    category = ServiceCategoryFactory()

    created = auth_client(customer).post(
        LIST_URL,
        {
            'master': master.id,
            'service_category': category.id,
            'problem_description': 'Akkumulyator o\'tirib qolgan',
            'customer_latitude': '41.311081',
            'customer_longitude': '69.240562',
            'offered_price': '150000.00',
        },
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    order_id = created.data['id']
    assert created.data['contact_unlocked'] is False

    master_client = auth_client(master.user)
    accepted = master_client.post(accept_url(order_id))
    assert accepted.status_code == status.HTTP_200_OK
    assert accepted.data['contact_unlocked'] is True

    completed = master_client.post(
        complete_url(order_id), {'final_price': '180000.00'}, format='json')
    assert completed.status_code == status.HTTP_200_OK
    assert completed.data['status'] == Order.Status.COMPLETED

    order = Order.objects.get(id=order_id)
    assert order.final_price == Decimal('180000.00')
