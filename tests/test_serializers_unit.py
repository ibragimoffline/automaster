
from decimal import Decimal

import pytest

from apps.locations.serializers import LocationSerializer
from apps.orders.serializers import OrderSerializer
from tests.factories import OrderFactory


class TestLocationSerializer:
    def test_valid_payload(self):
        serializer = LocationSerializer(data={
            'region': 'Toshkent',
            'district': 'Chilonzor',
            'address': 'Bunyodkor 1',
            'latitude': '41.311081',
            'longitude': '69.240562',
        })

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['latitude'] == Decimal('41.311081')

    def test_coordinates_are_required(self):
        serializer = LocationSerializer(data={'region': 'Toshkent'})

        assert not serializer.is_valid()
        assert 'latitude' in serializer.errors
        assert 'longitude' in serializer.errors

    def test_coordinates_only_is_enough(self):
        serializer = LocationSerializer(data={
            'latitude': '41.311081',
            'longitude': '69.240562',
        })

        assert serializer.is_valid(), serializer.errors

    def test_non_numeric_coordinates_rejected(self):
        serializer = LocationSerializer(data={'latitude': 'abc', 'longitude': 'xyz'})

        assert not serializer.is_valid()
        assert 'latitude' in serializer.errors

    def test_too_many_decimal_places_rejected(self):
        serializer = LocationSerializer(data={
            'latitude': '41.31108123456',
            'longitude': '69.240562',
        })

        assert not serializer.is_valid()
        assert 'latitude' in serializer.errors

    def test_optional_text_fields_may_be_blank(self):
        serializer = LocationSerializer(data={
            'region': '',
            'district': '',
            'address': '',
            'latitude': '41.311081',
            'longitude': '69.240562',
        })

        assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
class TestOrderSerializerWithoutRequest:

    def test_phones_are_hidden_without_request_context(self):
        order = OrderFactory(status='ACCEPTED')

        data = OrderSerializer(order).data

        assert data['customer_phone'] is None
        assert data['master_phone'] is None

    def test_contact_unlocked_still_computed_without_context(self):
        order = OrderFactory(status='ACCEPTED')

        assert OrderSerializer(order).data['contact_unlocked'] is True

    def test_negative_offered_price_rejected_by_validate(self):
        serializer = OrderSerializer()

        with pytest.raises(Exception) as exc:
            serializer.validate({'offered_price': Decimal('-1.00')})

        assert 'offered_price' in str(exc.value)

    def test_negative_final_price_rejected_by_validate(self):
        serializer = OrderSerializer()

        with pytest.raises(Exception) as exc:
            serializer.validate({'final_price': Decimal('-1.00')})

        assert 'final_price' in str(exc.value)

    def test_valid_prices_pass_validate(self):
        serializer = OrderSerializer()

        attrs = {'offered_price': Decimal('100.00'), 'final_price': Decimal('200.00')}

        assert serializer.validate(attrs) == attrs
