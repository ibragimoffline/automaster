from rest_framework import serializers
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
