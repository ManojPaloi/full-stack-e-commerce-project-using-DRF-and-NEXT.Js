from rest_framework import serializers
from .models import FastBanner, SecondBanner

class FastBannerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()  # Returns category name
    images = serializers.SerializerMethodField()  # Returns list of image URLs

    class Meta:
        model = FastBanner
        fields = [
            "title",
            "description",
            "images",
            "button_text",
            "discount_text",
            "category",
        ]

    def get_images(self, obj):
        if obj.image:
            return [obj.image.url]  # wrap single image in a list
        return []

class SecondBannerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = SecondBanner
        fields = [
            "title",
            "description",
            "images",
            "button_text",
            "discount_text",
            "category",
        ]

    def get_images(self, obj):
        if obj.image:
            return [obj.image.url]
        return []
