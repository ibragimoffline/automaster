from rest_framework import viewsets, exceptions, decorators, response
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'need_master_visit']

    def get_queryset(self):
        u = self.request.user
        qs = Order.objects.select_related('customer', 'master', 'master__user', 'service_category').prefetch_related('images')
        if u.role == u.Role.MASTER:
            return qs.filter(master__user=u)
        return qs.filter(customer=u)

    def perform_create(self, serializer):
        u = self.request.user
        if u.role != u.Role.CUSTOMER:
            raise exceptions.PermissionDenied('Faqat oddiy foydalanuvchi buyurtma bera oladi.')
        if not u.phone_verified:
            raise exceptions.PermissionDenied('Avval telefon raqamingizni tasdiqlang.')
        serializer.save(customer=u, status=Order.Status.PENDING)

    def _require_owner_master(self, order):
        if not (order.master and order.master.user_id == self.request.user.id):
            raise exceptions.PermissionDenied('Bu buyurtma sizga kelmagan.')

    @decorators.action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        order = self.get_object()
        self._require_owner_master(order)
        if order.status != Order.Status.PENDING:
            raise exceptions.ValidationError('Buyurtmani bu holatda qabul qilib bo\'lmaydi.')
        order.status = Order.Status.ACCEPTED
        order.save(update_fields=['status'])
        return response.Response(self.get_serializer(order).data)

    @decorators.action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        order = self.get_object()
        self._require_owner_master(order)

        if request.data.get('final_price') is not None:
            order.final_price = request.data['final_price']
        order.status = Order.Status.COMPLETED
        order.save(update_fields=['status', 'final_price'])
        return response.Response(self.get_serializer(order).data)
