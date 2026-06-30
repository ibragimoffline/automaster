from rest_framework import serializers

from .models import CarProblemImage, Order


class CarProblemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarProblemImage
        fields = [
            'id',
            'order',
            'image',
        ]
        read_only_fields = ['id']


# Aloqa ma'lumotlari faqat shu holatlarda ochiladi (buyurtma qabul qilingandan keyin)
CONTACT_UNLOCKED_STATUSES = ('ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS', 'COMPLETED')


class OrderSerializer(serializers.ModelSerializer):
    images = CarProblemImageSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    master_name = serializers.CharField(source='master.full_name', read_only=True)
    service_category_name = serializers.CharField(source='service_category.name', read_only=True)
    # Aloqa: faqat buyurtma qabul qilingach va faqat qarama-qarshi tomonga ko'rinadi.
    contact_unlocked = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    master_phone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'customer_username',
            'customer_phone',
            'master',
            'master_name',
            'master_phone',
            'service_category',
            'service_category_name',
            'problem_description',
            'customer_latitude',
            'customer_longitude',
            'customer_address',
            'need_master_visit',
            'status',
            'offered_price',
            'final_price',
            'contact_unlocked',
            'created_at',
            'images',
        ]

        read_only_fields = ['id', 'created_at', 'customer', 'status', 'final_price']

    def _request_user(self):
        req = self.context.get('request')
        return getattr(req, 'user', None) if req else None

    def get_contact_unlocked(self, obj):
        return obj.status in CONTACT_UNLOCKED_STATUSES

    def get_customer_phone(self, obj):
        """Mijoz raqami: mijozning o'ziga doim; ustaga faqat qabul qilingach."""
        user = self._request_user()
        if not user or not user.is_authenticated:
            return None
        if obj.customer_id == user.id:
            return obj.customer.phone
        is_owner_master = obj.master and obj.master.user_id == user.id
        if is_owner_master and obj.status in CONTACT_UNLOCKED_STATUSES:
            return obj.customer.phone
        return None

    def get_master_phone(self, obj):
        """Usta raqami: ustaning o'ziga doim; mijozga faqat qabul qilingach."""
        user = self._request_user()
        if not user or not user.is_authenticated or obj.master is None:
            return None
        if obj.master.user_id == user.id:
            return obj.master.user.phone
        if obj.customer_id == user.id and obj.status in CONTACT_UNLOCKED_STATUSES:
            return obj.master.user.phone
        return None

    def validate(self, attrs):
        price_from = attrs.get('offered_price')
        price_to = attrs.get('final_price')

        if price_from is not None and price_from < 0:
            raise serializers.ValidationError({'offered_price': 'Price cannot be negative.'})
        if price_to is not None and price_to < 0:
            raise serializers.ValidationError({'final_price': 'Price cannot be negative.'})

        return attrs
