from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.reviews.models import Review
from apps.services.models import MasterService

from .cache import invalidate_master_cache
from .models import MasterLike, MasterProfile, Workshop


@receiver([post_save, post_delete], sender=MasterLike)
def invalidate_like_cache(sender, instance, **kwargs):
    invalidate_master_cache(instance.master_id)


@receiver([post_save, post_delete], sender=Review)
def invalidate_review_cache(sender, instance, **kwargs):
    invalidate_master_cache(instance.master_id)


@receiver([post_save, post_delete], sender=MasterProfile)
def invalidate_profile_cache(sender, instance, **kwargs):
    invalidate_master_cache(instance.pk)


@receiver([post_save, post_delete], sender=Workshop)
@receiver([post_save, post_delete], sender=MasterService)
def invalidate_listing_cache(sender, instance, **kwargs):
    invalidate_master_cache(instance.master_id)
