from django.urls import path
from .views import ProductListCreateView, ProductDetailView, ReviewListCreateView

urlpatterns = [
    path("", ProductListCreateView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:product_id>/reviews/", ReviewListCreateView.as_view(), name="product-reviews"),

]
