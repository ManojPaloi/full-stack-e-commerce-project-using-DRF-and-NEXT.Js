from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer


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
    filterset_fields = ['category', 'is_new', 'is_available', 'free_delivery']
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

    def perform_update(self, serializer):
        """
        Ensure delivery_charge is correctly handled if free_delivery is checked
        """
        free_delivery = serializer.validated_data.get('free_delivery', None)
        if free_delivery:
            serializer.save(delivery_charge=0)
        else:
            # If delivery_charge is missing, set default 50
            delivery_charge = serializer.validated_data.get('delivery_charge', 50)
            serializer.save(delivery_charge=delivery_charge)


# --------------------------------------
# List/Create Reviews for a product
# --------------------------------------
class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/products/<product_id>/reviews/ -> List reviews for a product
    POST /api/products/<product_id>/reviews/ -> Add a new review
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_id'])

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        user = self.request.user

        # Prevent duplicate reviews
        if Review.objects.filter(product_id=product_id, user=user).exists():
            raise ValidationError("You have already reviewed this product.")

        serializer.save(product_id=product_id, user=user)
