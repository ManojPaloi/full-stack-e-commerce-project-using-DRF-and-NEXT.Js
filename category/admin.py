from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")  # removed 'slug'
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
