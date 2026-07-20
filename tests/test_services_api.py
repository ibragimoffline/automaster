from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from apps.services.models import MasterService, ServiceCategory
from tests.base import BaseAPITestCase
from tests.factories import (
    CustomerFactory,
    MasterProfileFactory,
    MasterServiceFactory,
    ServiceCategoryFactory,
)


class ServiceCategoryListAPITestCase(BaseAPITestCase):
    url = reverse('service-categories')

    def test_anonymous_can_list_categories(self):
        ServiceCategoryFactory(name='Dvigatel')
        ServiceCategoryFactory(name='Xodovoy')

        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_empty_list_when_no_categories(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_response_is_not_paginated(self):
        ServiceCategoryFactory()

        resp = self.client.get(self.url)

        self.assertIsInstance(resp.data, list)

    def test_sorted_by_master_count_desc(self):
        popular = ServiceCategoryFactory(name='Mashhur')
        quiet = ServiceCategoryFactory(name='Kamchil')
        for _ in range(3):
            MasterServiceFactory(category=popular, master=MasterProfileFactory())
        MasterServiceFactory(category=quiet, master=MasterProfileFactory())

        resp = self.client.get(self.url)

        self.assertEqual(resp.data[0]['name'], 'Mashhur')
        self.assertEqual(resp.data[1]['name'], 'Kamchil')

    def test_master_count_counts_distinct_masters(self):
        category = ServiceCategoryFactory(name='Dvigatel')
        master = MasterProfileFactory()
        MasterServiceFactory(category=category, master=master, title='Kapital')
        MasterServiceFactory(category=category, master=master, title='Diagnostika')

        resp = self.client.get(self.url)

        self.assertEqual(resp.data[0]['master_count'], 1)

    def test_ties_broken_by_name(self):
        ServiceCategoryFactory(name='Bbb')
        ServiceCategoryFactory(name='Aaa')

        resp = self.client.get(self.url)

        self.assertEqual([c['name'] for c in resp.data], ['Aaa', 'Bbb'])

    def test_category_with_no_services_has_zero_count(self):
        ServiceCategoryFactory(name='Bo\'sh')

        resp = self.client.get(self.url)

        self.assertEqual(resp.data[0]['master_count'], 0)


class MasterServiceListAPITestCase(BaseAPITestCase):
    url = reverse('master-services')

    def setUp(self):
        self.master_a = MasterProfileFactory(full_name='Usta A')
        self.master_b = MasterProfileFactory(full_name='Usta B')
        self.category = ServiceCategoryFactory(name='Dvigatel')
        self.service_a = MasterServiceFactory(
            master=self.master_a,
            category=self.category,
            title='Kapital ta\'mir',
            price_from=Decimal('500000.00'),
            price_to=Decimal('1500000.00'),
        )
        self.service_b = MasterServiceFactory(master=self.master_b, title='Moy almashtirish')

    def test_anonymous_can_list_services(self):
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_filter_by_master(self):
        resp = self.client.get(self.url, {'master': self.master_a.id})

        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['title'], 'Kapital ta\'mir')

    def test_filter_by_master_with_no_services_returns_empty(self):
        lonely = MasterProfileFactory()

        resp = self.client.get(self.url, {'master': lonely.id})

        self.assertEqual(resp.data, [])

    def test_service_payload_fields(self):
        resp = self.client.get(self.url, {'master': self.master_a.id})

        self.assertKeys(resp.data[0], ['id', 'master', 'category', 'title', 'price_from'])
        self.assertEqual(Decimal(resp.data[0]['price_from']), Decimal('500000.00'))

    def test_price_to_may_be_null(self):
        master = MasterProfileFactory()
        MasterServiceFactory(master=master, price_to=None)

        resp = self.client.get(self.url, {'master': master.id})

        self.assertIsNone(resp.data[0]['price_to'])



@pytest.mark.django_db
def test_service_category_str():
    category = ServiceCategoryFactory(name='Dvigatel')

    assert str(category) == 'Dvigatel'


@pytest.mark.django_db
def test_deleting_category_cascades_to_services():
    category = ServiceCategoryFactory()
    MasterServiceFactory(category=category)

    category.delete()

    assert MasterService.objects.count() == 0


@pytest.mark.django_db
def test_deleting_master_cascades_to_services():
    master = MasterProfileFactory()
    MasterServiceFactory(master=master)

    master.delete()

    assert MasterService.objects.count() == 0


@pytest.mark.django_db
def test_service_list_is_public_for_authenticated_user_too(auth_client):
    MasterServiceFactory()
    client = auth_client(CustomerFactory())

    resp = client.get(reverse('master-services'))

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_categories_endpoint_does_not_expose_write_methods(api_client):
    ServiceCategoryFactory()

    resp = api_client.post(reverse('service-categories'), {'name': 'Yangi'}, format='json')

    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert ServiceCategory.objects.count() == 1
