from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.routers import DefaultRouter

# Optional: if you have viewsets
router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'orders', OrderViewSet)

# API Root (overview of all apps)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        "accounts": request.build_absolute_uri("accounts/"),
        "category": request.build_absolute_uri("category/"),
        # Add more apps as needed
    })

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # Django admin dashboard
    # path("grappelli/", include("grappelli.urls")),  
    path("admin/", admin.site.urls),

    # API root (global entrypoint)
    path("api/", api_root, name="api-root"),

    # Browsable API login/logout
    path("api-auth/", include("rest_framework.urls")),

    # Accounts and category apps
    path("api/accounts/", include("accounts.urls")),
    path("api/category/", include("category.urls")),

    # Viewsets (only include if router has registered viewsets)
    # path("api/", include(router.urls)),  # Uncomment and adjust if viewsets are added
]



