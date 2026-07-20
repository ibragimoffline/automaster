from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Review
from .tasks import recalculate_master_rating


def dispatch_rating_recalculation(master_id):
    if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
        recalculate_master_rating.delay(master_id)
        return
    transaction.on_commit(
        lambda: recalculate_master_rating.delay(master_id)
    )


@receiver([post_save, post_delete], sender=Review)
def schedule_rating_recalculation(sender, instance, **kwargs):
    dispatch_rating_recalculation(instance.master_id)
