from django.db.models import Avg, Count
from rest_framework import viewsets, exceptions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.orders.models import Order
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # Sharhlarni ommaviy o'qish mumkin; yozish uchun avtorizatsiya kerak.
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'head', 'options']
    filterset_fields = ['master']

    def get_queryset(self):
        return Review.objects.select_related('customer', 'master')

    def perform_create(self, serializer):
        u = self.request.user
        order = serializer.validated_data['order']
        if order.customer_id != u.id:
            raise exceptions.PermissionDenied('Bu buyurtma sizniki emas.')
        if order.status != Order.Status.COMPLETED:
            raise exceptions.ValidationError('Reyting faqat yakunlangan buyurtmadan keyin beriladi.')
        if order.master is None or order.master.user_id == u.id:
            raise exceptions.ValidationError('Usta o\'ziga o\'zi sharh bera olmaydi.')
        if Review.objects.filter(order=order).exists():
            raise exceptions.ValidationError('Bitta buyurtmaga bitta sharh.')
        serializer.save(customer=u, master=order.master)
        self._recalc_rating(order.master)

    @staticmethod
    def _recalc_rating(master):
        agg = master.reviews.aggregate(avg=Avg('rating'), n=Count('id'))
        master.average_rating = agg['avg'] or 0
        master.total_reviews = agg['n']
        master.save(update_fields=['average_rating', 'total_reviews'])
