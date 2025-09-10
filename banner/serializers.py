from rest_framework import serializers
from .models import FirstBanner, SecondBanner


class FirstBannerSerializer(serializers.ModelSerializer):
    """
    Serializer for FirstBanner model.
    Includes an extra field `image_url` to provide
    the fully qualified URL for the banner image.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FirstBanner
        fields = "__all__"  # Includes: id, title, image, image_description, link_url, is_active, created_at

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class SecondBannerSerializer(serializers.ModelSerializer):
    """
    Serializer for SecondBanner model.
    Includes an extra field `image_url` to provide
    the fully qualified URL for the banner image.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SecondBanner
        fields = "__all__"  # Includes: id, title, image, image_description, link_url, is_active, created_at

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None
