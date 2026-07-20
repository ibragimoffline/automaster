import unittest
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.masters.views import haversine_km
from tests.base import BaseAPITestCase
from tests.factories import (
    MasterProfileFactory,
    MasterServiceFactory,
    ServiceCategoryFactory,
    WorkshopFactory,
)

TASHKENT = (41.311081, 69.240562)
SAMARKAND = (39.627012, 66.975000)


class NearbyMastersAPITestCase(BaseAPITestCase):
    url = reverse('nearby-masters')

    def setUp(self):
        self.near = MasterProfileFactory(full_name='Yaqin usta', average_rating=Decimal('4.00'))
        WorkshopFactory(
            master=self.near,
            latitude=Decimal('41.320000'),
            longitude=Decimal('69.250000'),
        )
        self.far = MasterProfileFactory(full_name='Uzoq usta', average_rating=Decimal('5.00'))
        WorkshopFactory(
            master=self.far,
            latitude=Decimal(str(SAMARKAND[0])),
            longitude=Decimal(str(SAMARKAND[1])),
        )

    def test_anonymous_can_list_masters(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_master_without_workshop_is_excluded(self):
        MasterProfileFactory(full_name='Ustaxonasiz usta')

        resp = self.client.get(self.url)

        names = [m['full_name'] for m in resp.data]
        self.assertNotIn('Ustaxonasiz usta', names)
        self.assertEqual(len(names), 2)

    def test_without_coords_sorted_by_rating_desc(self):
        resp = self.client.get(self.url)

        ratings = [float(m['average_rating']) for m in resp.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        self.assertEqual(resp.data[0]['full_name'], 'Uzoq usta')

    def test_without_coords_distance_is_null(self):
        resp = self.client.get(self.url)

        self.assertTrue(all(m['distance_km'] is None for m in resp.data))

    def test_with_coords_sorted_by_distance(self):
        resp = self.client.get(self.url, {'lat': TASHKENT[0], 'lng': TASHKENT[1]})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]['full_name'], 'Yaqin usta')
        self.assertEqual(resp.data[1]['full_name'], 'Uzoq usta')

    def test_with_coords_distance_is_computed(self):
        resp = self.client.get(self.url, {'lat': TASHKENT[0], 'lng': TASHKENT[1]})

        near, far = resp.data[0], resp.data[1]
        self.assertLess(near['distance_km'], 5)
        self.assertGreater(far['distance_km'], 200)

    def test_distance_is_rounded_to_one_decimal(self):
        resp = self.client.get(self.url, {'lat': TASHKENT[0], 'lng': TASHKENT[1]})

        for m in resp.data:
            self.assertEqual(round(m['distance_km'], 1), m['distance_km'])

    def test_equal_distance_falls_back_to_rating(self):
        low = MasterProfileFactory(full_name='Past reyting', average_rating=Decimal('3.00'))
        WorkshopFactory(master=low, latitude=Decimal('55.000000'), longitude=Decimal('55.000000'))
        high = MasterProfileFactory(full_name='Yuqori reyting', average_rating=Decimal('4.90'))
        WorkshopFactory(master=high, latitude=Decimal('55.000000'), longitude=Decimal('55.000000'))

        resp = self.client.get(self.url, {'lat': 55.0, 'lng': 55.0})

        names = [m['full_name'] for m in resp.data]
        self.assertLess(names.index('Yuqori reyting'), names.index('Past reyting'))

    def test_visiting_filter_returns_only_visiting_masters(self):
        visiting = MasterProfileFactory(full_name='Boradigan usta', can_visit_customer=True)
        WorkshopFactory(master=visiting)

        resp = self.client.get(self.url, {'visiting': 'true'})

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['full_name'], 'Boradigan usta')

    def test_visiting_filter_ignored_when_not_true(self):
        resp = self.client.get(self.url, {'visiting': 'false'})

        self.assertEqual(len(resp.data), 2)

    def test_visiting_filter_combines_with_coords(self):
        visiting = MasterProfileFactory(full_name='Boradigan usta', can_visit_customer=True)
        WorkshopFactory(
            master=visiting,
            latitude=Decimal('41.315000'),
            longitude=Decimal('69.245000'),
        )

        resp = self.client.get(
            self.url, {'visiting': 'true', 'lat': TASHKENT[0], 'lng': TASHKENT[1]})

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['full_name'], 'Boradigan usta')
        self.assertIsNotNone(resp.data[0]['distance_km'])

    def test_only_lat_without_lng_is_ignored(self):
        resp = self.client.get(self.url, {'lat': TASHKENT[0]})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(all(m['distance_km'] is None for m in resp.data))

    def test_response_contains_nested_workshop(self):
        resp = self.client.get(self.url)

        workshop = resp.data[0]['workshop']
        self.assertIsNotNone(workshop)
        self.assertKeys(workshop, ['name', 'region', 'district', 'latitude', 'longitude'])

    def test_specialties_are_deduplicated_and_capped_at_three(self):
        category = ServiceCategoryFactory(name='Dvigatel')
        MasterServiceFactory(master=self.near, category=category)
        MasterServiceFactory(master=self.near, category=category)
        for name in ('Xodovoy', 'Elektrika', 'Kuzov'):
            MasterServiceFactory(
                master=self.near, category=ServiceCategoryFactory(name=name))

        resp = self.client.get(self.url, {'lat': TASHKENT[0], 'lng': TASHKENT[1]})

        specialties = resp.data[0]['specialties']
        self.assertEqual(len(specialties), 3)
        self.assertEqual(len(set(specialties)), 3)
        self.assertEqual(specialties[0], 'Dvigatel')

    @unittest.expectedFailure
    def test_invalid_coords_should_return_400(self):
        resp = self.client.get(self.url, {'lat': 'abc', 'lng': 'xyz'})

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class MasterDetailAPITestCase(BaseAPITestCase):
    def setUp(self):
        self.master = MasterProfileFactory(full_name='Aniq usta', experience_years=12)
        WorkshopFactory(master=self.master, name='Aniq servis')

    def test_anonymous_can_retrieve_master(self):
        resp = self.client.get(reverse('master-detail', args=[self.master.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['full_name'], 'Aniq usta')
        self.assertEqual(resp.data['experience_years'], 12)
        self.assertEqual(resp.data['workshop']['name'], 'Aniq servis')

    def test_master_without_workshop_is_still_retrievable(self):
        solo = MasterProfileFactory(full_name='Ustaxonasiz')

        resp = self.client.get(reverse('master-detail', args=[solo.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data['workshop'])

    def test_unknown_master_returns_404(self):
        resp = self.client.get(reverse('master-detail', args=[999999]))

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_distance_is_null(self):
        resp = self.client.get(reverse('master-detail', args=[self.master.id]))

        self.assertIsNone(resp.data['distance_km'])


def test_haversine_same_point_is_zero():
    assert haversine_km(*TASHKENT, *TASHKENT) == pytest.approx(0.0, abs=1e-9)


def test_haversine_is_symmetric():
    forward = haversine_km(*TASHKENT, *SAMARKAND)
    backward = haversine_km(*SAMARKAND, *TASHKENT)

    assert forward == pytest.approx(backward)


def test_haversine_tashkent_to_samarkand():
    assert haversine_km(*TASHKENT, *SAMARKAND) == pytest.approx(270, abs=15)


def test_haversine_one_degree_latitude_is_about_111km():
    assert haversine_km(0, 0, 1, 0) == pytest.approx(111.19, abs=0.5)


def test_haversine_antipodal_points_is_half_circumference():
    assert haversine_km(0, 0, 0, 180) == pytest.approx(20015, abs=5)


@pytest.mark.django_db
def test_master_profile_defaults():
    master = MasterProfileFactory(is_verified=False)

    assert master.average_rating == Decimal('0.00')
    assert master.total_reviews == 0
    assert master.can_visit_customer is False
    assert master.is_verified is False
