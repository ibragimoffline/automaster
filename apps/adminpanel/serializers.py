from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.masters.models import MasterProfile
from apps.orders.models import Order
from apps.services.models import ServiceCategory
from apps.reviews.models import Review

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    orders_count = serializers.IntegerField(read_only=True, required=False)
    is_master_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'phone',
            'role', 'phone_verified', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'orders_count', 'is_master_verified',
        ]
        
        read_only_fields = ['id', 'username', 'date_joined', 'is_superuser']

    def get_is_master_verified(self, obj):
        mp = getattr(obj, 'master_profile', None)
        return mp.is_verified if mp else None


class AdminMasterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    workshop_name = serializers.CharField(source='workshop.name', read_only=True, default=None)
    district = serializers.CharField(source='workshop.district', read_only=True, default=None)

    class Meta:
        model = MasterProfile
        fields = [
            'id', 'username', 'phone', 'full_name', 'experience_years', 'bio',
            'is_verified', 'can_visit_customer', 'average_rating', 'total_reviews',
            'workshop_name', 'district',
        ]
        read_only_fields = ['id', 'average_rating', 'total_reviews']


class AdminOrderSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    master_name = serializers.CharField(source='master.full_name', read_only=True, default=None)
    master_phone = serializers.CharField(source='master.user.phone', read_only=True, default=None)
    service_category_name = serializers.CharField(source='service_category.name', read_only=True, default=None)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_username', 'customer_phone', 'master', 'master_name', 'master_phone',
            'service_category', 'service_category_name', 'problem_description',
            'customer_address', 'need_master_visit', 'status',
            'offered_price', 'final_price', 'created_at',
        ]

        read_only_fields = ['id', 'customer_username', 'customer_phone', 'created_at']


class AdminCategorySerializer(serializers.ModelSerializer):
    master_count = serializers.IntegerField(read_only=True, required=False)
    service_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'master_count', 'service_count']
        read_only_fields = ['id']


class AdminReviewSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    master_name = serializers.CharField(source='master.full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'customer_username', 'master', 'master_name', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = fields
