from django.contrib import admin
from .models import FastBanner, SecondBanner

@admin.register(FastBanner)
class FastBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "description", "category__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

@admin.register(SecondBanner)
class SecondBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "description", "category__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
