from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderItemCreateView,
    OrderItemDeleteView,
    PaymentCreateView,
)

urlpatterns = [
    # Orders
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),

    # Order Items
    path("<int:order_id>/items/add/", OrderItemCreateView.as_view(), name="orderitem-add"),
    path("items/<int:pk>/delete/", OrderItemDeleteView.as_view(), name="orderitem-delete"),

    # Payments
    path("<int:order_id>/payment/", PaymentCreateView.as_view(), name="payment-create"),
]
