from rest_framework import generics, permissions
from .models import Category
from .serializers import CategorySerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories
    POST: Create a new category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a category by ID
    PUT/PATCH: Update a category
    DELETE: Delete a category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
