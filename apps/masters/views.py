from math import radians, cos, sin, asin, sqrt

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import MasterProfile
from .serializers import MasterProfileSerializer


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


class NearbyMastersAPIView(ListAPIView):
    serializer_class = MasterProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = (MasterProfile.objects
              .select_related('workshop', 'user')
              .prefetch_related('services__category')  # specialties uchun
              .filter(workshop__isnull=False))

        # Chiqib borish xizmati bor ustalarni alohida filter qilish: ?visiting=true
        if self.request.query_params.get('visiting') == 'true':
            qs = qs.filter(can_visit_customer=True)

        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        if lat and lng:
            lat, lng = float(lat), float(lng)
            masters = list(qs)
            for m in masters:
                m.distance_km = haversine_km(
                    lat, lng, float(m.workshop.latitude), float(m.workshop.longitude))
            # Avval masofa bo'yicha, keyin reyting bo'yicha saralash.
            masters.sort(key=lambda m: (m.distance_km, -float(m.average_rating)))
            return masters
        return qs.order_by('-average_rating')


class MasterDetailAPIView(RetrieveAPIView):
    """Bitta usta profili — frontend usta sahifasi uchun."""
    serializer_class = MasterProfileSerializer
    permission_classes = [AllowAny]
    queryset = (MasterProfile.objects
                .select_related('workshop', 'user')
                .prefetch_related('services__category'))
