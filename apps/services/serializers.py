from rest_framework import serializers

from .models import MasterService, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    master_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = ServiceCategory
        fields = [
            'id',
            'name',
            'description',
            'master_count',
        ]
        read_only_fields = ['id']


class MasterServiceSerializer(serializers.ModelSerializer):
    category_detail = ServiceCategorySerializer(source='category', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    master_name = serializers.CharField(source='master.full_name', read_only=True)

    class Meta:
        model = MasterService
        fields = [
            'id',
            'master',
            'master_name',
            'category',
            'category_detail',
            'category_name',
            'title',
            'price_from',
            'price_to',
            'description',
        ]
        read_only_fields = ['id']
