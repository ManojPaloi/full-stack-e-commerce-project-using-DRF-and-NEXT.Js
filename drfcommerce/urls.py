from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

# Optional: register viewsets here if needed
router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'orders', OrderViewSet)

# ✅ API Root (overview of all apps)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        "accounts": request.build_absolute_uri("accounts/"),
        "category": request.build_absolute_uri("category/"),
        "banners": request.build_absolute_uri("banners/"),  # updated key for clarity
        "products": request.build_absolute_uri("products/"),

    })

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # ✅ Django admin panel
    path("admin/", admin.site.urls),

    # ✅ API root overview
    path("api/", api_root, name="api-root"),

    # ✅ Browsable API login/logout
    path("api-auth/", include("rest_framework.urls")),

    # ✅ Application endpoints
    path("api/accounts/", include("accounts.urls")),
    path("api/category/", include("category.urls")),
    path("api/banners/", include("banner.urls")),
    path("api/products/", include("products.urls")),

    # Optional: DRF router endpoints (if using viewsets)
    # path("api/", include(router.urls)),
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
