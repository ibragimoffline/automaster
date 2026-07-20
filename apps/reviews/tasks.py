from celery import shared_task
from django.db import OperationalError
from django.db.models import Avg, Count

from apps.masters.cache import invalidate_master_cache
from apps.masters.models import MasterProfile

from .models import Review


@shared_task(
    autoretry_for=(OperationalError,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def recalculate_master_rating(master_id):
    if not MasterProfile.objects.filter(pk=master_id).exists():
        return {'master_id': master_id, 'updated': False}

    values = Review.objects.filter(master_id=master_id).aggregate(
        average=Avg('rating'),
        total=Count('id'),
    )
    average = values['average'] or 0
    MasterProfile.objects.filter(pk=master_id).update(
        average_rating=average,
        total_reviews=values['total'],
    )
    invalidate_master_cache(master_id)
    return {
        'master_id': master_id,
        'updated': True,
        'average_rating': str(average),
        'total_reviews': values['total'],
    }
