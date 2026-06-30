from django.urls import path
from .views import NearbyMastersAPIView, MasterDetailAPIView

urlpatterns = [
    path('nearby/', NearbyMastersAPIView.as_view(), name='nearby-masters'),
    path('<int:pk>/', MasterDetailAPIView.as_view(), name='master-detail'),
]
