from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Product, Review
from .serializers import ReviewSerializer


# --------------------------------------
# List all products or create a new one
# --------------------------------------
class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/      -> List all products
    POST /api/products/      -> Create a new product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_new', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']  # Default ordering: newest first

# --------------------------------------
# Retrieve, update, or delete a product
# --------------------------------------
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/products/<pk>/ -> Retrieve a product
    PUT    /api/products/<pk>/ -> Update a product
    PATCH  /api/products/<pk>/ -> Partial update
    DELETE /api/products/<pk>/ -> Delete a product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]








class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/<product_id>/reviews/ -> List reviews for a product
    POST /api/products/<product_id>/reviews/ -> Add a new review
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_id'])

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        user = self.request.user
        # Prevent duplicate reviews
        if Review.objects.filter(product_id=product_id, user=user).exists():
            raise ValidationError("You have already reviewed this product.")
        serializer.save(product_id=product_id, user=user)
