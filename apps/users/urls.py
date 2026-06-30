from django.urls import path

from .views import MeView, RegisterView, VerifyPhoneView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
]
