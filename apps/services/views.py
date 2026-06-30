from django.db.models import Count
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import ServiceCategory, MasterService
from .serializers import ServiceCategorySerializer, MasterServiceSerializer


class ServiceCategoryListAPIView(ListAPIView):
    """Xizmat kategoriyalari + har biri bo'yicha usta soni."""
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (ServiceCategory.objects
                .annotate(master_count=Count('master_services__master', distinct=True))
                .order_by('-master_count', 'name'))


class MasterServiceListAPIView(ListAPIView):
    """Usta xizmatlari ro'yxati. ?master=<id> bo'yicha filtrlanadi."""
    serializer_class = MasterServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = MasterService.objects.select_related('category', 'master')
        master = self.request.query_params.get('master')
        if master:
            qs = qs.filter(master_id=master)
        return qs
