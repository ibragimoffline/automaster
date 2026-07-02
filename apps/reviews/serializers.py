from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    master_name = serializers.CharField(source='master.full_name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'customer',
            'customer_username',
            'master',
            'master_name',
            'order',
            'rating',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'customer', 'master']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('1 dan 5 gacha baholanishi shart')
        return value
