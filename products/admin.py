# products/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Review

# --------------------------------------
# Inline Review Admin
# --------------------------------------
class ReviewInline(admin.TabularInline):
    """
    Inline display of reviews in the Product admin page.
    - Shows user, rating, and comment
    - Prevents adding new reviews from admin (optional)
    """
    model = Review
    fields = ('user', 'rating', 'comment', 'created_at')
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    extra = 0  # don't show empty rows
    can_delete = False


# --------------------------------------
# Product Admin
# --------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Modern Product admin:
    - Image thumbnails
    - Color swatches with tooltip
    - Discount percentage badge
    - NEW badge
    - Inline reviews
    - Search and filters
    """

    list_display = (
        'thumbnail',
        'name',
        'category',
        'price',
        'discount_price',
        'discount_badge',
        'stock',
        'is_new_badge',
        'is_available',
        'display_colors',
        'created_at',
    )

    list_filter = ('is_new', 'is_available', 'category', 'colors', 'created_at')
    search_fields = ('name', 'description', 'category__name', 'colors')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('thumbnail', 'discount_badge', 'is_new_badge')
    inlines = [ReviewInline]

    # ----------------------------
    # Thumbnail preview
    # ----------------------------
    def thumbnail(self, obj):
        """Display small product image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:50px; border-radius:4px;" />',
                obj.image.url
            )
        return "—"
    thumbnail.short_description = "Image Preview"

    # ----------------------------
    # Display color swatches
    # ----------------------------
    def display_colors(self, obj):
        """Display colors as visual swatches with tooltip."""
        if obj.colors:
            badges = ""
            for color in obj.colors:
                badges += f'<span style="display:inline-block; width:15px; height:15px; background:{color}; margin-right:3px; border:1px solid #ccc;" title="{color}"></span>'
            return format_html(badges)
        return "—"
    display_colors.short_description = "Colors"

    # ----------------------------
    # Discount badge
    # ----------------------------
    def discount_badge(self, obj):
        """Show discount percentage badge."""
        if obj.is_on_sale:
            return format_html(
                '<span style="color:white; background:red; padding:2px 5px; border-radius:3px;">-{}%</span>',
                int(obj.discount_percentage)
            )
        return "—"
    discount_badge.short_description = "Discount"

    # ----------------------------
    # New product badge
    # ----------------------------
    def is_new_badge(self, obj):
        """Highlight new products."""
        if obj.is_new:
            return format_html(
                '<span style="color:white; background:green; padding:2px 5px; border-radius:3px;">NEW</span>'
            )
        return "—"
    is_new_badge.short_description = "New Product"


# --------------------------------------
# Review Admin
# --------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Review admin:
    - Show product, user, rating, comment, created date
    - Filter and search easily
    """
    list_display = ('product', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)
