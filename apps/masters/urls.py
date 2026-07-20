from django.urls import path
from .views import (
    MasterCommentsAPIView,
    MasterDetailAPIView,
    MasterLikeAPIView,
    NearbyMastersAPIView,
)

urlpatterns = [
    path('nearby/', NearbyMastersAPIView.as_view(), name='nearby-masters'),
    path('<int:pk>/comments/', MasterCommentsAPIView.as_view(), name='master-comments'),
    path('<int:pk>/like/', MasterLikeAPIView.as_view(), name='master-like'),
    path('<int:pk>/', MasterDetailAPIView.as_view(), name='master-detail'),
]
