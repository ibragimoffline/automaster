from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from rest_framework import viewsets, filters, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.masters.models import MasterProfile
from apps.orders.models import Order
from apps.services.models import ServiceCategory
from apps.reviews.models import Review

from .permissions import IsAdmin
from .serializers import (
    AdminUserSerializer, AdminMasterSerializer, AdminOrderSerializer,
    AdminCategorySerializer, AdminReviewSerializer,
)

User = get_user_model()


class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['date_joined', 'username', 'role']
    ordering = ['-date_joined']

    def get_queryset(self):
        qs = (User.objects
              .select_related('master_profile')
              .annotate(orders_count=Count('orders', distinct=True)))
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs

    def perform_destroy(self, instance):
        if instance.id == self.request.user.id:
            raise exceptions.ValidationError('O\'z hisobingizni o\'chira olmaysiz.')
        if instance.is_superuser:
            raise exceptions.ValidationError('Superuser hisobini o\'chirib bo\'lmaydi.')
        instance.delete()

    def perform_update(self, serializer):
        
        if serializer.instance.id == self.request.user.id:
            data = serializer.validated_data
            if data.get('role') and data['role'] != serializer.instance.role:
                raise exceptions.ValidationError('O\'z rolingizni o\'zgartira olmaysiz.')
            if data.get('is_active') is False:
                raise exceptions.ValidationError('O\'zingizni bloklab bo\'lmaydi.')
        serializer.save()


class AdminMasterViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminMasterSerializer
    http_method_names = ['get', 'patch', 'head', 'options']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'user__username', 'user__phone', 'workshop__name']
    ordering_fields = ['average_rating', 'total_reviews', 'experience_years']
    ordering = ['-average_rating']

    def get_queryset(self):
        qs = MasterProfile.objects.select_related('user', 'workshop')
        verified = self.request.query_params.get('verified')
        if verified in ('true', 'false'):
            qs = qs.filter(is_verified=(verified == 'true'))
        return qs


class AdminOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminOrderSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['problem_description', 'customer__username', 'master__full_name']
    ordering_fields = ['created_at', 'status', 'offered_price']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Order.objects.select_related('customer', 'master', 'master__user', 'service_category')
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class AdminCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminCategorySerializer
    pagination_class = None

    def get_queryset(self):
        return (ServiceCategory.objects
                .annotate(
                    master_count=Count('master_services__master', distinct=True),
                    service_count=Count('master_services', distinct=True))
                .order_by('name'))


class AdminReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = AdminReviewSerializer
    http_method_names = ['get', 'delete', 'head', 'options']
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.select_related('customer', 'master')

    def perform_destroy(self, instance):
        master = instance.master
        instance.delete()

        from django.db.models import Avg
        agg = master.reviews.aggregate(avg=Avg('rating'), n=Count('id'))
        master.average_rating = round(agg['avg'], 2) if agg['avg'] else 0
        master.total_reviews = agg['n']
        master.save(update_fields=['average_rating', 'total_reviews'])


class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        status_counts = dict(
            Order.objects.values_list('status').annotate(n=Count('id')))
        revenue = (Order.objects.filter(status='COMPLETED')
                   .aggregate(s=Sum('final_price'))['s'] or 0)
        recent = (Order.objects
                  .select_related('customer', 'master', 'service_category')
                  .order_by('-created_at')[:8])
        return Response({
            'users': {
                'total': User.objects.count(),
                'customers': User.objects.filter(role='CUSTOMER').count(),
                'masters': User.objects.filter(role='MASTER').count(),
                'admins': User.objects.filter(role='ADMIN').count(),
            },
            'masters': {
                'total': MasterProfile.objects.count(),
                'verified': MasterProfile.objects.filter(is_verified=True).count(),
                'visiting': MasterProfile.objects.filter(can_visit_customer=True).count(),
            },
            'orders': {
                'total': Order.objects.count(),
                'by_status': status_counts,
            },
            'reviews': Review.objects.count(),
            'categories': ServiceCategory.objects.count(),
            'revenue': float(revenue),
            'recent_orders': AdminOrderSerializer(recent, many=True).data,
        })
