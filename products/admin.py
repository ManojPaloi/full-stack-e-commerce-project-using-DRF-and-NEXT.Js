from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Review

# --------------------------------------
# Product Admin
# --------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail',
        'name',
        'category',
        'price',
        'discount_price',
        'stock',
        'is_new',
        'is_available',
        'created_at',
    )
    list_filter = ('is_new', 'is_available', 'category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('thumbnail',)

    def thumbnail(self, obj):
        """Show a small image preview in the admin list and form."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:50px;" />',
                obj.image.url
            )
        return "—"
    thumbnail.short_description = "Image Preview"


# --------------------------------------
# Review Admin (if you added reviews)
# --------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)
