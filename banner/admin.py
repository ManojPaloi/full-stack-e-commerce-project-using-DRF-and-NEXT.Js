from django.contrib import admin
from .models import FirstBanner, SecondBanner

@admin.register(FirstBanner)
class FirstBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "preview_image", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "image_description")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Banner Info", {
            "fields": ("title", "image", "image_description", "link_url")
        }),
        ("Status & Metadata", {
            "fields": ("is_active", "created_at"),
            "classes": ("collapse",),
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height:40px;border-radius:4px;" />'
        return "No Image"
    preview_image.allow_tags = True
    preview_image.short_description = "Preview"


@admin.register(SecondBanner)
class SecondBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "preview_image", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "image_description")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Banner Info", {
            "fields": ("title", "image", "image_description", "link_url")
        }),
        ("Status & Metadata", {
            "fields": ("is_active", "created_at"),
            "classes": ("collapse",),
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height:40px;border-radius:4px;" />'
        return "No Image"
    preview_image.allow_tags = True
    preview_image.short_description = "Preview"
