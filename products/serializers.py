from rest_framework import serializers
from .models import Product, Review

# --------------------------------------
# Review Serializer
# --------------------------------------
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # show username

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']


# --------------------------------------
# Product Serializer
# --------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)  # nested reviews
    total_reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'name',
            'slug',
            'description',
            'price',
            'discount_price',
            'delivery_charge',
            'free_delivery',
            'stock',
            'image',
            'colors',
            'is_available',
            'is_new',
            'rating',
            'created_at',
            'updated_at',
            'reviews',
            'total_reviews',
            'average_rating',
        ]
        read_only_fields = ['created_at', 'updated_at', 'rating', 'total_reviews', 'average_rating']

    def get_total_reviews(self, obj):
        """Return total number of reviews for this product."""
        return obj.reviews.count()

    def get_average_rating(self, obj):
        """Return average rating for this product based on reviews."""
        total = obj.reviews.count()
        if total == 0:
            return 0
        return round(sum([review.rating for review in obj.reviews.all()]) / total, 2)

    def validate(self, data):
        """
        Ensure that delivery_charge is 0 if free_delivery is True.
        """
        if data.get('free_delivery', False):
            data['delivery_charge'] = 0
        else:
            if 'delivery_charge' not in data or data['delivery_charge'] is None:
                data['delivery_charge'] = 50.00  # default
        return data
