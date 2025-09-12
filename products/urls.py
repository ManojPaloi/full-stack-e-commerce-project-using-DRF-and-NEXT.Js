from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ReviewListCreateView

urlpatterns = [
    # Product endpoints
    path("", ProductListCreateView.as_view(), name="product-list"),  # /api/products/
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),  # /api/products/<id>/

    # Review endpoints
    path("<int:product_id>/reviews/", ReviewListCreateView.as_view(), name="product-reviews"),  # /api/products/<id>/reviews/
]
