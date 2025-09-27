from rest_framework import serializers
from .models import FastBanner, SecondBanner

class FastBannerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = FastBanner
        fields = ["title", "description", "images", "button_text", "discount_text", "category"]

    def get_images(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request:
                url = request.build_absolute_uri(url)
            return [url]
        return []

class SecondBannerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = SecondBanner
        fields = ["title", "description", "images", "button_text", "discount_text", "category"]

    def get_images(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request:
                url = request.build_absolute_uri(url)
            return [url]
        return []
