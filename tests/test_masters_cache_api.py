from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

from apps.masters.cache import (
    invalidate_master_cache,
    master_comment_count_key,
    master_like_count_key,
)
from apps.masters.models import MasterLike, MasterProfile
from tests.base import BaseAPITestCase
from tests.factories import CustomerFactory, MasterProfileFactory, ReviewFactory, WorkshopFactory


class MasterListingCacheAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master = MasterProfileFactory(full_name='Cache usta')
        WorkshopFactory(master=self.master)

    def test_listing_response_is_cached(self):
        url = reverse('nearby-masters')
        first = self.client.get(url)
        MasterProfile.objects.filter(pk=self.master.pk).update(full_name='Yangi nom')

        second = self.client.get(url)
        self.assertEqual(second.data[0]['full_name'], first.data[0]['full_name'])

        invalidate_master_cache(self.master.pk)
        third = self.client.get(url)
        self.assertEqual(third.data[0]['full_name'], 'Yangi nom')

    def test_detail_populates_cached_counts(self):
        user = CustomerFactory()
        MasterLike.objects.create(user=user, master=self.master)
        ReviewFactory(master=self.master, comment='Yaxshi xizmat')

        resp = self.client.get(reverse('master-detail', args=[self.master.pk]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['like_count'], 1)
        self.assertEqual(resp.data['comment_count'], 1)
        self.assertEqual(cache.get(master_like_count_key(self.master.pk)), 1)
        self.assertEqual(cache.get(master_comment_count_key(self.master.pk)), 1)

    def test_counts_are_invalidated_after_changes(self):
        url = reverse('nearby-masters')
        initial = self.client.get(url)
        self.assertEqual(initial.data[0]['like_count'], 0)
        self.assertEqual(initial.data[0]['comment_count'], 0)

        MasterLike.objects.create(user=CustomerFactory(), master=self.master)
        ReviewFactory(master=self.master, comment='Yangi izoh')

        updated = self.client.get(url)
        self.assertEqual(updated.data[0]['like_count'], 1)
        self.assertEqual(updated.data[0]['comment_count'], 1)


class MasterCommentsCacheAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master = MasterProfileFactory()
        self.reviews = [
            ReviewFactory(master=self.master, comment=f'Izoh {index}')
            for index in range(12)
        ]
        self.url = reverse('master-comments', args=[self.master.pk])

    def test_returns_latest_ten_comments(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 10)
        self.assertEqual(resp.data[0]['id'], self.reviews[-1].id)
        self.assertEqual(resp.data[-1]['id'], self.reviews[-10].id)

    def test_empty_comments_are_excluded(self):
        ReviewFactory(master=self.master, comment='')

        resp = self.client.get(self.url)

        self.assertTrue(all(item['comment'] for item in resp.data))

    def test_new_comment_invalidates_cache(self):
        first = self.client.get(self.url)
        newest = ReviewFactory(master=self.master, comment='Eng yangi izoh')

        second = self.client.get(self.url)

        self.assertNotEqual(first.data[0]['id'], second.data[0]['id'])
        self.assertEqual(second.data[0]['id'], newest.id)

    def test_unknown_listing_returns_404(self):
        resp = self.client.get(reverse('master-comments', args=[999999]))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class MasterLikeAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master = MasterProfileFactory()
        self.user = CustomerFactory()
        self.url = reverse('master-like', args=[self.master.pk])

    def test_authentication_is_required(self):
        resp = self.client.post(self.url)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_toggles_like(self):
        self.auth(self.user)

        liked = self.client.post(self.url)
        self.assertEqual(liked.status_code, status.HTTP_200_OK)
        self.assertTrue(liked.data['liked'])
        self.assertEqual(liked.data['like_count'], 1)
        self.assertEqual(MasterLike.objects.count(), 1)

        unliked = self.client.post(self.url)
        self.assertFalse(unliked.data['liked'])
        self.assertEqual(unliked.data['like_count'], 0)
        self.assertEqual(MasterLike.objects.count(), 0)

    def test_get_returns_current_like_status(self):
        self.auth(self.user)
        MasterLike.objects.create(user=self.user, master=self.master)

        resp = self.client.get(self.url)

        self.assertTrue(resp.data['liked'])
        self.assertEqual(resp.data['like_count'], 1)

    def test_user_can_like_listing_only_once(self):
        self.auth(self.user)
        self.client.post(self.url)
        self.client.get(self.url)

        self.assertEqual(MasterLike.objects.filter(
            user=self.user,
            master=self.master,
        ).count(), 1)
