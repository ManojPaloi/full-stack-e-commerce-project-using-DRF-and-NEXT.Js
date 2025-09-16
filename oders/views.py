from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer


# ------------------------------
# Order Views
# ------------------------------
class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET: List all orders for the authenticated user.
    POST: Create a new order.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).select_related("coupon").prefetch_related("items")

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve an order.
    PUT/PATCH: Update status or details.
    DELETE: Cancel order.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


# ------------------------------
# Order Item Views
# ------------------------------
class OrderItemCreateView(generics.CreateAPIView):
    """
    POST: Add an item to an order.
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderItemDeleteView(generics.DestroyAPIView):
    """
    DELETE: Remove an item from an order.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


# ------------------------------
# Payment Views
# ------------------------------
class PaymentCreateView(APIView):
    """
    POST: Record payment for an order.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer=request.user)
        if hasattr(order, "payment"):
            return Response({"detail": "Payment already recorded."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order, amount=order.final_price)
            order.status = "processing"
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
