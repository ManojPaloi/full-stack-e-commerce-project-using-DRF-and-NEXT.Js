"""
Project-level URL Configuration for drfcommerce.

This routes all the top-level endpoints of the project:
- Admin dashboard
- DRF's browsable API login/logout
- Accounts app (authentication, registration, profile, JWT)
- Global API root overview
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

# Optional: if you have viewsets
router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'orders', OrderViewSet)


# 👇 API Root (overview of all apps)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        "accounts": request.build_absolute_uri("accounts/"),
        # Later if you add more apps, just add them here
        # "products": request.build_absolute_uri("products/"),
        # "orders": request.build_absolute_uri("orders/"),
    })


urlpatterns = [
    # Django admin dashboard
    path("admin/", admin.site.urls),

    # API root (global entrypoint)
    path("api/", api_root, name="api-root"),

    # Browsable API login/logout
    # path("api-auth/", include("rest_framework.urls")),

    # Accounts app
    path("api/accounts/", include("accounts.urls")),

    # If you add viewsets (products, orders, etc.)
    path("api/", include(router.urls)),
]
