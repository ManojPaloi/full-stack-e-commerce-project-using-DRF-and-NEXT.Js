from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')          # Show only name and slug
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug from name
