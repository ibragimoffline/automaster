from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.masters.models import MasterProfile
from apps.orders.models import Order
from apps.reviews.models import Review
from apps.services.models import ServiceCategory
from tests.base import BaseAPITestCase
from tests.factories import (
    AdminUserFactory,
    CustomerFactory,
    MasterProfileFactory,
    MasterServiceFactory,
    MasterUserFactory,
    OrderFactory,
    ReviewFactory,
    ServiceCategoryFactory,
    UserFactory,
    WorkshopFactory,
)

User = get_user_model()

STATS_URL = reverse('admin-stats')
USERS_URL = reverse('admin-user-list')
MASTERS_URL = reverse('admin-master-list')
ORDERS_URL = reverse('admin-order-list')
CATEGORIES_URL = reverse('admin-category-list')
REVIEWS_URL = reverse('admin-review-list')

PROTECTED_URLS = [STATS_URL, USERS_URL, MASTERS_URL, ORDERS_URL, CATEGORIES_URL, REVIEWS_URL]


class AdminPermissionAPITestCase(BaseAPITestCase):
    def test_anonymous_is_rejected_everywhere(self):
        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_is_forbidden_everywhere(self):
        self.auth(CustomerFactory())

        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_master_is_forbidden_everywhere(self):
        self.auth(MasterUserFactory())

        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_role_is_allowed(self):
        self.auth(AdminUserFactory())

        for url in PROTECTED_URLS:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_superuser_without_admin_role_is_allowed(self):
        self.auth(UserFactory(is_superuser=True, role=User.Role.CUSTOMER))

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class AdminUserViewSetAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.admin = AdminUserFactory(username='bosh_admin')
        self.auth(self.admin)
        self.customer = CustomerFactory(username='mijoz1', first_name='Sardor')
        self.master_user = MasterUserFactory(username='usta1')

    def detail(self, user):
        return reverse('admin-user-detail', args=[user.id])

    def test_lists_all_users(self):
        resp = self.client.get(USERS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), User.objects.count())

    def test_filter_by_role(self):
        resp = self.client.get(USERS_URL, {'role': User.Role.MASTER})

        self.assertEqual([u['username'] for u in resp.data], ['usta1'])

    def test_search_by_first_name(self):
        resp = self.client.get(USERS_URL, {'search': 'Sardor'})

        self.assertEqual([u['username'] for u in resp.data], ['mijoz1'])

    def test_search_by_phone(self):
        resp = self.client.get(USERS_URL, {'search': self.customer.phone})

        self.assertEqual([u['username'] for u in resp.data], ['mijoz1'])

    def test_orders_count_is_annotated(self):
        OrderFactory(customer=self.customer)
        OrderFactory(customer=self.customer)

        resp = self.client.get(USERS_URL, {'search': 'mijoz1'})

        self.assertEqual(resp.data[0]['orders_count'], 2)

    def test_is_master_verified_is_null_for_plain_user(self):
        resp = self.client.get(USERS_URL, {'search': 'mijoz1'})

        self.assertIsNone(resp.data[0]['is_master_verified'])

    def test_is_master_verified_reflects_profile(self):
        MasterProfileFactory(user=self.master_user, is_verified=True)

        resp = self.client.get(USERS_URL, {'search': 'usta1'})

        self.assertTrue(resp.data[0]['is_master_verified'])

    def test_default_ordering_is_newest_first(self):
        resp = self.client.get(USERS_URL)

        joined = [u['date_joined'] for u in resp.data]
        self.assertEqual(joined, sorted(joined, reverse=True))

    def test_can_change_another_users_role(self):
        resp = self.client.patch(
            self.detail(self.customer), {'role': User.Role.MASTER}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, User.Role.MASTER)

    def test_can_deactivate_another_user(self):
        resp = self.client.patch(
            self.detail(self.customer), {'is_active': False}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)

    def test_cannot_change_own_role(self):
        resp = self.client.patch(
            self.detail(self.admin), {'role': User.Role.CUSTOMER}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, User.Role.ADMIN)

    def test_setting_own_role_to_same_value_is_allowed(self):
        resp = self.client.patch(
            self.detail(self.admin), {'role': User.Role.ADMIN}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cannot_deactivate_self(self):
        resp = self.client.patch(self.detail(self.admin), {'is_active': False}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_cannot_delete_self(self):
        resp = self.client.delete(self.detail(self.admin))

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=self.admin.id).exists())

    def test_cannot_delete_superuser(self):
        root = UserFactory(username='root', is_superuser=True)

        resp = self.client.delete(self.detail(root))

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=root.id).exists())

    def test_can_delete_regular_user(self):
        resp = self.client.delete(self.detail(self.customer))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.customer.id).exists())

    def test_username_is_read_only(self):
        resp = self.client.patch(
            self.detail(self.customer), {'username': 'yangi_nom'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.username, 'mijoz1')

    def test_post_is_not_allowed(self):
        resp = self.client.post(USERS_URL, {'username': 'x'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_is_not_allowed(self):
        resp = self.client.put(self.detail(self.customer), {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminMasterViewSetAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.auth(AdminUserFactory())
        self.verified = MasterProfileFactory(
            full_name='Tasdiqlangan usta', is_verified=True, average_rating=Decimal('4.50'))
        self.unverified = MasterProfileFactory(
            full_name='Tasdiqlanmagan usta', is_verified=False, average_rating=Decimal('3.00'))

    def test_lists_masters_sorted_by_rating(self):
        resp = self.client.get(MASTERS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]['full_name'], 'Tasdiqlangan usta')

    def test_filter_verified_true(self):
        resp = self.client.get(MASTERS_URL, {'verified': 'true'})

        self.assertEqual([m['full_name'] for m in resp.data], ['Tasdiqlangan usta'])

    def test_filter_verified_false(self):
        resp = self.client.get(MASTERS_URL, {'verified': 'false'})

        self.assertEqual([m['full_name'] for m in resp.data], ['Tasdiqlanmagan usta'])

    def test_invalid_verified_value_is_ignored(self):
        resp = self.client.get(MASTERS_URL, {'verified': 'maybe'})

        self.assertEqual(len(resp.data), 2)

    def test_search_by_workshop_name(self):
        WorkshopFactory(master=self.verified, name='Chilonzor servis')

        resp = self.client.get(MASTERS_URL, {'search': 'Chilonzor'})

        self.assertEqual([m['full_name'] for m in resp.data], ['Tasdiqlangan usta'])

    def test_admin_can_verify_master(self):
        resp = self.client.patch(
            reverse('admin-master-detail', args=[self.unverified.id]),
            {'is_verified': True},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.unverified.refresh_from_db()
        self.assertTrue(self.unverified.is_verified)

    def test_average_rating_is_read_only(self):
        resp = self.client.patch(
            reverse('admin-master-detail', args=[self.unverified.id]),
            {'average_rating': '5.00'},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.unverified.refresh_from_db()
        self.assertEqual(self.unverified.average_rating, Decimal('3.00'))

    def test_workshop_name_is_null_without_workshop(self):
        resp = self.client.get(MASTERS_URL, {'verified': 'false'})

        self.assertIsNone(resp.data[0]['workshop_name'])

    def test_delete_is_not_allowed(self):
        resp = self.client.delete(reverse('admin-master-detail', args=[self.verified.id]))

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(MasterProfile.objects.count(), 2)


class AdminOrderViewSetAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.auth(AdminUserFactory())
        self.pending = OrderFactory(
            status=Order.Status.PENDING, problem_description='Dvigatel shovqini')
        self.completed = OrderFactory(
            status=Order.Status.COMPLETED, final_price=Decimal('500000.00'))

    def test_admin_sees_every_order(self):
        resp = self.client.get(ORDERS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_filter_by_status(self):
        resp = self.client.get(ORDERS_URL, {'status': Order.Status.COMPLETED})

        self.assertEqual([o['id'] for o in resp.data], [self.completed.id])

    def test_search_by_problem_description(self):
        resp = self.client.get(ORDERS_URL, {'search': 'shovqini'})

        self.assertEqual([o['id'] for o in resp.data], [self.pending.id])

    def test_default_ordering_is_newest_first(self):
        resp = self.client.get(ORDERS_URL)

        self.assertEqual(resp.data[0]['id'], self.completed.id)

    def test_admin_sees_phones_regardless_of_status(self):
        resp = self.client.get(ORDERS_URL, {'status': Order.Status.PENDING})

        self.assertEqual(resp.data[0]['customer_phone'], self.pending.customer.phone)
        self.assertEqual(resp.data[0]['master_phone'], self.pending.master.user.phone)

    def test_admin_can_change_order_status(self):
        resp = self.client.patch(
            reverse('admin-order-detail', args=[self.pending.id]),
            {'status': Order.Status.CANCELLED},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, Order.Status.CANCELLED)

    def test_admin_can_delete_order(self):
        resp = self.client.delete(reverse('admin-order-detail', args=[self.pending.id]))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 1)

    def test_post_is_not_allowed(self):
        resp = self.client.post(ORDERS_URL, {}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminCategoryViewSetAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.auth(AdminUserFactory())
        self.category = ServiceCategoryFactory(name='Dvigatel')

    def test_lists_categories_sorted_by_name(self):
        ServiceCategoryFactory(name='Akkumulyator')

        resp = self.client.get(CATEGORIES_URL)

        self.assertEqual([c['name'] for c in resp.data], ['Akkumulyator', 'Dvigatel'])

    def test_counts_are_annotated(self):
        master = MasterProfileFactory()
        MasterServiceFactory(master=master, category=self.category, title='Kapital')
        MasterServiceFactory(master=master, category=self.category, title='Diagnostika')

        resp = self.client.get(CATEGORIES_URL)

        row = next(c for c in resp.data if c['name'] == 'Dvigatel')
        self.assertEqual(row['master_count'], 1)
        self.assertEqual(row['service_count'], 2)

    def test_admin_can_create_category(self):
        resp = self.client.post(
            CATEGORIES_URL, {'name': 'Kuzov', 'description': 'Kuzov ishlari'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ServiceCategory.objects.filter(name='Kuzov').exists())

    def test_admin_can_rename_category(self):
        resp = self.client.patch(
            reverse('admin-category-detail', args=[self.category.id]),
            {'name': 'Motor'},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Motor')

    def test_admin_can_delete_category(self):
        resp = self.client.delete(reverse('admin-category-detail', args=[self.category.id]))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ServiceCategory.objects.count(), 0)

    def test_name_is_required(self):
        resp = self.client.post(CATEGORIES_URL, {'description': 'nomsiz'}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', resp.data)


class AdminReviewViewSetAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.auth(AdminUserFactory())
        self.master = MasterProfileFactory()
        self.review = ReviewFactory(master=self.master, rating=5)

    def test_lists_reviews(self):
        resp = self.client.get(REVIEWS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['master_name'], self.master.full_name)

    def test_admin_can_delete_review(self):
        resp = self.client.delete(reverse('admin-review-detail', args=[self.review.id]))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_deleting_review_recalculates_master_rating(self):
        ReviewFactory(master=self.master, rating=3)
        self.master.average_rating = Decimal('4.00')
        self.master.total_reviews = 2
        self.master.save(update_fields=['average_rating', 'total_reviews'])

        self.client.delete(reverse('admin-review-detail', args=[self.review.id]))

        self.master.refresh_from_db()
        self.assertEqual(self.master.average_rating, Decimal('3.00'))
        self.assertEqual(self.master.total_reviews, 1)

    def test_deleting_last_review_resets_rating_to_zero(self):
        self.master.average_rating = Decimal('5.00')
        self.master.total_reviews = 1
        self.master.save(update_fields=['average_rating', 'total_reviews'])

        self.client.delete(reverse('admin-review-detail', args=[self.review.id]))

        self.master.refresh_from_db()
        self.assertEqual(self.master.average_rating, Decimal('0.00'))
        self.assertEqual(self.master.total_reviews, 0)

    def test_patch_is_not_allowed(self):
        resp = self.client.patch(
            reverse('admin-review-detail', args=[self.review.id]), {'rating': 1}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_is_not_allowed(self):
        resp = self.client.post(REVIEWS_URL, {'rating': 5}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminStatsAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.auth(self.admin)

    def test_empty_database_stats(self):
        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['users']['total'], 1)
        self.assertEqual(resp.data['users']['admins'], 1)
        self.assertEqual(resp.data['masters']['total'], 0)
        self.assertEqual(resp.data['orders']['total'], 0)
        self.assertEqual(resp.data['orders']['by_status'], {})
        self.assertEqual(resp.data['reviews'], 0)
        self.assertEqual(resp.data['revenue'], 0)
        self.assertEqual(resp.data['recent_orders'], [])

    def test_user_counts_by_role(self):
        CustomerFactory()
        CustomerFactory()
        MasterUserFactory()

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['users']['total'], 4)
        self.assertEqual(resp.data['users']['customers'], 2)
        self.assertEqual(resp.data['users']['masters'], 1)
        self.assertEqual(resp.data['users']['admins'], 1)

    def test_master_counts(self):
        MasterProfileFactory(is_verified=True, can_visit_customer=True)
        MasterProfileFactory(is_verified=False, can_visit_customer=False)

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['masters']['total'], 2)
        self.assertEqual(resp.data['masters']['verified'], 1)
        self.assertEqual(resp.data['masters']['visiting'], 1)

    def test_orders_grouped_by_status(self):
        OrderFactory(status=Order.Status.PENDING)
        OrderFactory(status=Order.Status.PENDING)
        OrderFactory(status=Order.Status.COMPLETED)

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['orders']['total'], 3)
        self.assertEqual(resp.data['orders']['by_status']['PENDING'], 2)
        self.assertEqual(resp.data['orders']['by_status']['COMPLETED'], 1)

    def test_revenue_sums_completed_orders_only(self):
        OrderFactory(status=Order.Status.COMPLETED, final_price=Decimal('300000.00'))
        OrderFactory(status=Order.Status.COMPLETED, final_price=Decimal('200000.00'))
        OrderFactory(status=Order.Status.PENDING, final_price=Decimal('999999.00'))

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['revenue'], 500000.0)

    def test_revenue_ignores_completed_orders_without_price(self):
        OrderFactory(status=Order.Status.COMPLETED, final_price=None)

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['revenue'], 0)

    def test_recent_orders_capped_at_eight_and_newest_first(self):
        orders = [OrderFactory() for _ in range(10)]

        resp = self.client.get(STATS_URL)

        recent_ids = [o['id'] for o in resp.data['recent_orders']]
        self.assertEqual(len(recent_ids), 8)
        self.assertEqual(recent_ids, [o.id for o in reversed(orders)][:8])

    def test_counts_reviews_and_categories(self):
        ReviewFactory()
        ServiceCategoryFactory()
        ServiceCategoryFactory()

        resp = self.client.get(STATS_URL)

        self.assertEqual(resp.data['reviews'], 1)
        self.assertGreaterEqual(resp.data['categories'], 2)



@pytest.mark.django_db
@pytest.mark.parametrize(
    'factory_cls,allowed',
    [
        (AdminUserFactory, True),
        (CustomerFactory, False),
        (MasterUserFactory, False),
    ],
)
def test_stats_access_per_role(auth_client, factory_cls, allowed):
    resp = auth_client(factory_cls()).get(STATS_URL)

    expected = status.HTTP_200_OK if allowed else status.HTTP_403_FORBIDDEN
    assert resp.status_code == expected


@pytest.mark.django_db
def test_is_admin_permission_object():
    from apps.adminpanel.permissions import IsAdmin

    class Request:
        pass

    request = Request()
    request.user = AdminUserFactory()

    assert IsAdmin().has_permission(request, None) is True
