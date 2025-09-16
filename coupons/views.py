from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Coupon
from .serializers import CouponSerializer
from oders.models import Order

# -------------------------------------------------
# List and Create Coupons (Admin Only)
# -------------------------------------------------
class CouponListCreateView(generics.ListCreateAPIView):
    """
    GET: List all coupons (staff only)
    POST: Create a new coupon (staff only)
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------------------------------
# Retrieve, Update, Delete Coupon (Admin Only)
# -------------------------------------------------
class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET, PUT, PATCH, DELETE: Manage a single coupon (staff only)
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------------------------------------
# Apply Coupon to an Order
# -------------------------------------------------
class ApplyCouponView(APIView):
    """
    POST: Apply a coupon to an order.
    Request data:
        {
            "order_id": 1,
            "code": "DISCOUNT10"
        }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        order_id = request.data.get("order_id")

        if not code or not order_id:
            return Response(
                {"detail": "Coupon code and order_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate coupon
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response(
                {"detail": "Invalid coupon code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if coupon is active and not expired
        if not coupon.active:
            return Response({"detail": "This coupon is inactive."}, status=400)
        if coupon.valid_from > timezone.now():
            return Response({"detail": "This coupon is not yet valid."}, status=400)
        if coupon.valid_to < timezone.now():
            return Response({"detail": "This coupon has expired."}, status=400)

        # Get the order
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Apply discount
        discount = (coupon.discount / 100) * order.total_price
        final_price = order.total_price - discount
        if final_price < 0:
            final_price = 0

        order.final_price = final_price
        order.save()

        return Response(
            {
                "detail": "Coupon applied successfully.",
                "order_id": order.id,
                "original_price": order.total_price,
                "discount": float(discount),
                "final_price": float(final_price),
            },
            status=status.HTTP_200_OK,
        )
