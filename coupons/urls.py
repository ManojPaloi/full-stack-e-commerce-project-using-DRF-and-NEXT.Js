# coupons/urls.py

from django.urls import path
from .views import CouponListCreateView, CouponDetailView, ApplyCouponView

app_name = "coupons"  # ✅ Required for namespacing

urlpatterns = [
    path("", CouponListCreateView.as_view(), name="coupon-list-create"),
    path("<int:pk>/", CouponDetailView.as_view(), name="coupon-detail"),
    path("apply/", ApplyCouponView.as_view(), name="apply-coupon"),
]
