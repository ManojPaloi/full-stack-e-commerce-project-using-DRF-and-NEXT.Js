from rest_framework import serializers
from .models import Product, Review, Category

# -------------------------------
# Review Serializer
# -------------------------------
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.get_full_name", default="Anonymous")
    image = serializers.SerializerMethodField()
    content = serializers.CharField(source="comment")
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        model = Review
        fields = ["content", "rating", "author", "image", "date"]

    def get_image(self, obj):
        # assuming user profile has image or return placeholder
        if hasattr(obj.user, "profile") and obj.user.profile.image:
            return obj.user.profile.image.url
        return "/images/people/person.jpg"

# -------------------------------
# Product Serializer
# -------------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()  # category name
    reviews = ReviewSerializer(many=True, read_only=True)
    total_reviews = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    aboutItem = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "description",
            "aboutItem",
            "price",
            "discount",
            "rating",
            "stockItems",
            "reviews",
            "brand",
            "color",
            "images",
        ]

    def get_total_reviews(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        total = obj.reviews.count()
        if total == 0:
            return 0
        return round(sum([r.rating for r in obj.reviews.all()]) / total, 2)

    def get_images(self, obj):
        # assuming obj.image is main image and obj.other_images is JSONField or list of images
        image_list = []
        if obj.image:
            image_list.append(obj.image.url)
        if hasattr(obj, "other_images") and obj.other_images:
            image_list.extend([img.url if hasattr(img, "url") else img for img in obj.other_images])
        return image_list

    def get_color(self, obj):
        # assuming color is JSONField or comma-separated string
        if hasattr(obj, "colors") and obj.colors:
            if isinstance(obj.colors, list):
                return obj.colors
            return [c.strip() for c in obj.colors.split(",")]
        return []

    def get_aboutItem(self, obj):
        # assuming aboutItem is a JSONField list or can be generated
        return obj.aboutItem if hasattr(obj, "aboutItem") else []
