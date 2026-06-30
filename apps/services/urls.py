from django.urls import path
from .views import ServiceCategoryListAPIView, MasterServiceListAPIView

urlpatterns = [
    path('categories/', ServiceCategoryListAPIView.as_view(), name='service-categories'),
    path('', MasterServiceListAPIView.as_view(), name='master-services'),
]
