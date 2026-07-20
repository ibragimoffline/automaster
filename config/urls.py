from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from apps.users.views import CustomTokenObtainPairView
from apps.orders.views import OrderViewSet
from apps.reviews.views import ReviewViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/auth/', include('apps.users.urls')),
    path('api/masters/', include('apps.masters.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/admin/', include('apps.adminpanel.urls')),
    path('api/', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
