from decimal import Decimal

import pytest

from apps.reviews.tasks import recalculate_master_rating
from tests.factories import MasterProfileFactory, ReviewFactory


@pytest.mark.django_db
def test_rating_task_recalculates_average_and_total():
    master = MasterProfileFactory()
    ReviewFactory(master=master, rating=5)
    ReviewFactory(master=master, rating=3)

    result = recalculate_master_rating(master.pk)

    master.refresh_from_db()
    assert master.average_rating == Decimal('4.00')
    assert master.total_reviews == 2
    assert result['updated'] is True
    assert result['total_reviews'] == 2


@pytest.mark.django_db
def test_review_delete_triggers_rating_recalculation():
    master = MasterProfileFactory()
    first = ReviewFactory(master=master, rating=5)
    ReviewFactory(master=master, rating=3)

    first.delete()

    master.refresh_from_db()
    assert master.average_rating == Decimal('3.00')
    assert master.total_reviews == 1


@pytest.mark.django_db
def test_rating_task_handles_missing_master():
    result = recalculate_master_rating(999999)

    assert result == {'master_id': 999999, 'updated': False}
