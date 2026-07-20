from rest_framework import serializers
from django.core.cache import cache

from .cache import (
    cache_ttl,
    master_comment_count_key,
    master_like_count_key,
)
from .models import MasterProfile, Workshop


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = [
            'id',
            'master',
            'name',
            'region',
            'district',
            'address',
            'latitude',
            'longitude',
            'open_time',
            'close_time',
        ]
        read_only_fields = ['id']


class MasterProfileSerializer(serializers.ModelSerializer):
    workshop = WorkshopSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    distance_km = serializers.SerializerMethodField()
    specialties = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = MasterProfile
        fields = [
            'id',
            'user',
            'username',
            'full_name',
            'experience_years',
            'bio',
            'is_verified',
            'can_visit_customer',
            'average_rating',
            'total_reviews',
            'like_count',
            'comment_count',
            'workshop',
            'distance_km',
            'specialties',
        ]
        read_only_fields = ['id', 'average_rating', 'total_reviews', 'is_verified']

    def get_distance_km(self, obj):
        d = getattr(obj, 'distance_km', None)
        return round(d, 1) if d is not None else None

    def get_specialties(self, obj):
        seen, out = set(), []
        for s in obj.services.all():
            name = s.category.name if s.category_id else None
            if name and name not in seen:
                seen.add(name)
                out.append(name)
        return out[:3]

    def get_like_count(self, obj):
        key = master_like_count_key(obj.pk)
        value = cache.get(key)
        if value is None:
            value = getattr(obj, 'like_count_db', None)
            if value is None:
                value = obj.likes.count()
            cache.set(key, value, cache_ttl())
        return value

    def get_comment_count(self, obj):
        key = master_comment_count_key(obj.pk)
        value = cache.get(key)
        if value is None:
            value = getattr(obj, 'comment_count_db', None)
            if value is None:
                value = obj.reviews.exclude(comment='').count()
            cache.set(key, value, cache_ttl())
        return value
