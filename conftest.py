
import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from tests.factories import (
    AdminUserFactory,
    CustomerFactory,
    MasterProfileFactory,
    OrderFactory,
    ServiceCategoryFactory,
    WorkshopFactory,
)


@pytest.fixture(autouse=True)
def clear_django_cache():
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    def _make(user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    return _make


@pytest.fixture
def customer(db):
    return CustomerFactory()


@pytest.fixture
def unverified_customer(db):
    return CustomerFactory(phone_verified=False)


@pytest.fixture
def master_profile(db):
    return MasterProfileFactory()


@pytest.fixture
def workshop(db, master_profile):
    return WorkshopFactory(master=master_profile)


@pytest.fixture
def admin_user(db):
    return AdminUserFactory()


@pytest.fixture
def category(db):
    return ServiceCategoryFactory(name='Dvigatel')


@pytest.fixture
def order(db, customer, master_profile, category):
    return OrderFactory(customer=customer, master=master_profile, service_category=category)
