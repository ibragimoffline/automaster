from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.orders.models import Order
from apps.reviews.models import Review
from tests.base import BaseAPITestCase
from tests.factories import (
    CustomerFactory,
    MasterProfileFactory,
    OrderFactory,
    ReviewFactory,
)

LIST_URL = reverse('review-list')


def completed_order(customer, master):
    return OrderFactory(customer=customer, master=master, status=Order.Status.COMPLETED)


class ReviewCreateAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.master = MasterProfileFactory()
        self.order = completed_order(self.customer, self.master)

    def payload(self, **overrides):
        data = {'order': self.order.id, 'rating': 5, 'comment': 'Ajoyib ish!'}
        data.update(overrides)
        return data

    def test_anonymous_cannot_create_review(self):
        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 0)

    def test_customer_reviews_completed_order(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get()
        self.assertEqual(review.customer, self.customer)
        self.assertEqual(review.master, self.master)
        self.assertEqual(review.rating, 5)

    def test_master_is_taken_from_order_not_payload(self):
        impostor = MasterProfileFactory()
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(master=impostor.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.get().master, self.master)

    def test_customer_is_taken_from_request(self):
        other = CustomerFactory()
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(customer=other.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.get().customer, self.customer)

    def test_cannot_review_someone_elses_order(self):
        self.auth(CustomerFactory())

        resp = self.client.post(LIST_URL, self.payload(), format='json')

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_review_unfinished_order(self):
        pending = OrderFactory(
            customer=self.customer, master=self.master, status=Order.Status.PENDING)
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(order=pending.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_review_order_without_master(self):
        masterless = OrderFactory(
            customer=self.customer, master=None, status=Order.Status.COMPLETED)
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(order=masterless.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_master_cannot_review_themselves(self):
        self_order = OrderFactory(
            customer=self.master.user, master=self.master, status=Order.Status.COMPLETED)
        self.auth(self.master.user)

        resp = self.client.post(LIST_URL, self.payload(order=self_order.id), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 0)

    def test_one_review_per_order(self):
        self.auth(self.customer)
        first = self.client.post(LIST_URL, self.payload(), format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(LIST_URL, self.payload(rating=1), format='json')

        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_below_one_rejected(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(rating=0), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', resp.data)

    def test_rating_above_five_rejected(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(rating=6), format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', resp.data)

    def test_missing_order_rejected(self):
        self.auth(self.customer)
        data = self.payload()
        del data['order']

        resp = self.client.post(LIST_URL, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('order', resp.data)

    def test_comment_is_optional(self):
        self.auth(self.customer)

        resp = self.client.post(LIST_URL, self.payload(comment=''), format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class ReviewRatingRecalcAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master = MasterProfileFactory()

    def leave_review(self, rating):
        customer = CustomerFactory()
        order = completed_order(customer, self.master)
        self.auth(customer)
        return self.client.post(
            LIST_URL, {'order': order.id, 'rating': rating}, format='json')

    def test_first_review_sets_average_and_count(self):
        self.leave_review(4)

        self.master.refresh_from_db()
        self.assertEqual(self.master.average_rating, Decimal('4.00'))
        self.assertEqual(self.master.total_reviews, 1)

    def test_average_across_multiple_reviews(self):
        self.leave_review(5)
        self.leave_review(3)

        self.master.refresh_from_db()
        self.assertEqual(self.master.average_rating, Decimal('4.00'))
        self.assertEqual(self.master.total_reviews, 2)

    def test_average_is_rounded_to_two_decimals(self):
        for rating in (5, 4, 4):
            self.leave_review(rating)

        self.master.refresh_from_db()
        self.assertEqual(self.master.average_rating, Decimal('4.33'))
        self.assertEqual(self.master.total_reviews, 3)

    def test_other_masters_rating_untouched(self):
        other = MasterProfileFactory(average_rating=Decimal('0.00'))
        self.leave_review(5)

        other.refresh_from_db()
        self.assertEqual(other.average_rating, Decimal('0.00'))
        self.assertEqual(other.total_reviews, 0)


class ReviewListAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master_a = MasterProfileFactory(full_name='Usta A')
        self.master_b = MasterProfileFactory(full_name='Usta B')
        self.review_a = ReviewFactory(master=self.master_a, rating=5)
        self.review_b = ReviewFactory(master=self.master_b, rating=3)

    def test_anonymous_can_read_reviews(self):
        resp = self.client.get(LIST_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_filter_by_master(self):
        resp = self.client.get(LIST_URL, {'master': self.master_a.id})

        self.assertEqual([r['id'] for r in resp.data], [self.review_a.id])

    def test_retrieve_single_review(self):
        resp = self.client.get(reverse('review-detail', args=[self.review_a.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['rating'], 5)
        self.assertEqual(resp.data['master_name'], 'Usta A')
        self.assertEqual(resp.data['customer_username'], self.review_a.customer.username)

    def test_put_is_not_allowed(self):
        self.auth(self.review_a.customer)

        resp = self.client.put(
            reverse('review-detail', args=[self.review_a.id]), {'rating': 1}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_is_not_allowed(self):
        self.auth(self.review_a.customer)

        resp = self.client.patch(
            reverse('review-detail', args=[self.review_a.id]), {'rating': 1}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_is_not_allowed(self):
        self.auth(self.review_a.customer)

        resp = self.client.delete(reverse('review-detail', args=[self.review_a.id]))

        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Review.objects.count(), 2)



@pytest.mark.django_db
@pytest.mark.parametrize('rating', [1, 2, 3, 4, 5])
def test_valid_ratings_accepted(auth_client, rating):
    customer = CustomerFactory()
    order = completed_order(customer, MasterProfileFactory())

    resp = auth_client(customer).post(
        LIST_URL, {'order': order.id, 'rating': rating}, format='json')

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize('rating', [0, -1, 6, 100])
def test_out_of_range_ratings_rejected(auth_client, rating):
    customer = CustomerFactory()
    order = completed_order(customer, MasterProfileFactory())

    resp = auth_client(customer).post(
        LIST_URL, {'order': order.id, 'rating': rating}, format='json')

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert Review.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'order_status',
    [
        Order.Status.PENDING,
        Order.Status.ACCEPTED,
        Order.Status.ON_THE_WAY,
        Order.Status.IN_PROGRESS,
        Order.Status.CANCELLED,
        Order.Status.REJECTED,
    ],
)
def test_only_completed_orders_can_be_reviewed(auth_client, order_status):
    customer = CustomerFactory()
    order = OrderFactory(
        customer=customer, master=MasterProfileFactory(), status=order_status)

    resp = auth_client(customer).post(
        LIST_URL, {'order': order.id, 'rating': 5}, format='json')

    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_order_has_one_to_one_review():
    review = ReviewFactory()

    assert review.order.review == review


@pytest.mark.django_db
def test_deleting_order_cascades_to_review():
    review = ReviewFactory()

    review.order.delete()

    assert Review.objects.count() == 0
