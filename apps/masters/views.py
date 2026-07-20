from math import radians, cos, sin, asin, sqrt

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer

from .cache import (
    cache_ttl,
    master_comments_key,
    master_detail_key,
    master_like_count_key,
    master_list_key,
)
from .models import MasterLike, MasterProfile
from .serializers import MasterProfileSerializer


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


class NearbyMastersAPIView(ListAPIView):
    serializer_class = MasterProfileSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        key = master_list_key(request.query_params.urlencode())
        data = cache.get(key)
        if data is not None:
            return Response(data)
        result = super().list(request, *args, **kwargs)
        cache.set(key, result.data, cache_ttl())
        return result

    def get_queryset(self):
        qs = (MasterProfile.objects
              .select_related('workshop', 'user')
              .prefetch_related('services__category')
              .annotate(
                  like_count_db=Count('likes', distinct=True),
                  comment_count_db=Count(
                      'reviews',
                      filter=~Q(reviews__comment=''),
                      distinct=True,
                  ),
              )
              .filter(workshop__isnull=False))

        
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
            
            masters.sort(key=lambda m: (m.distance_km, -float(m.average_rating)))
            return masters
        return qs.order_by('-average_rating')


class MasterDetailAPIView(RetrieveAPIView):
    serializer_class = MasterProfileSerializer
    permission_classes = [AllowAny]
    queryset = (MasterProfile.objects
                .select_related('workshop', 'user')
                .prefetch_related('services__category')
                .annotate(
                    like_count_db=Count('likes', distinct=True),
                    comment_count_db=Count(
                        'reviews',
                        filter=~Q(reviews__comment=''),
                        distinct=True,
                    ),
                ))

    def retrieve(self, request, *args, **kwargs):
        key = master_detail_key(kwargs['pk'])
        data = cache.get(key)
        if data is not None:
            return Response(data)
        result = super().retrieve(request, *args, **kwargs)
        cache.set(key, result.data, cache_ttl())
        return result


class MasterCommentsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        key = master_comments_key(pk)
        data = cache.get(key)
        if data is not None:
            return Response(data)
        get_object_or_404(MasterProfile, pk=pk)
        comments = (Review.objects
                    .filter(master_id=pk)
                    .exclude(comment='')
                    .select_related('customer', 'master')
                    .order_by('-created_at')[:10])
        data = ReviewSerializer(comments, many=True).data
        cache.set(key, data, cache_ttl())
        return Response(data)


class MasterLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        master = get_object_or_404(MasterProfile, pk=pk)
        liked = MasterLike.objects.filter(user=request.user, master=master).exists()
        count = self._like_count(master)
        return Response({'liked': liked, 'like_count': count})

    @transaction.atomic
    def post(self, request, pk):
        master = get_object_or_404(MasterProfile, pk=pk)
        like, created = MasterLike.objects.get_or_create(
            user=request.user,
            master=master,
        )
        if not created:
            like.delete()
        count = master.likes.count()
        cache.set(master_like_count_key(master.pk), count, cache_ttl())
        return Response({'liked': created, 'like_count': count})

    @staticmethod
    def _like_count(master):
        key = master_like_count_key(master.pk)
        count = cache.get(key)
        if count is None:
            count = master.likes.count()
            cache.set(key, count, cache_ttl())
        return count
