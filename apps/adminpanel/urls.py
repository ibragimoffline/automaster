from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserViewSet, AdminMasterViewSet, AdminOrderViewSet,
    AdminCategoryViewSet, AdminReviewViewSet, AdminStatsView,
)

router = DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin-user')
router.register('masters', AdminMasterViewSet, basename='admin-master')
router.register('orders', AdminOrderViewSet, basename='admin-order')
router.register('categories', AdminCategoryViewSet, basename='admin-category')
router.register('reviews', AdminReviewViewSet, basename='admin-review')

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('', include(router.urls)),
]
