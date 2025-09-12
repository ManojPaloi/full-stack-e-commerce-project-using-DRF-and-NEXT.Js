from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Review

# Inline Review Admin
class ReviewInline(admin.TabularInline):
    model = Review
    fields = ('user', 'rating', 'comment', 'created_at')
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    extra = 0
    can_delete = False

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'name', 'category', 'price', 'discount_price',
        'delivery_charge', 'free_delivery',
        'discount_badge', 'stock', 'is_new_badge', 'is_available', 'display_colors', 'created_at'
    )

    fields = (
        'category', 'name', 'slug', 'description', 'price', 'discount_price',
        'free_delivery', 'delivery_charge',
        'stock', 'image', 'colors',
        'is_available', 'is_new', 'rating'
    )

    inlines = [ReviewInline]
    readonly_fields = ('thumbnail', 'discount_badge', 'is_new_badge')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.free_delivery:
            readonly.append('delivery_charge')
        return readonly

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px; max-width:50px; border-radius:4px;" />',
                obj.image.url
            )
        return "—"
    thumbnail.short_description = "Image Preview"

    def display_colors(self, obj):
        if obj.colors:
            badges = ""
            for color in obj.colors:
                badges += f'<span style="display:inline-block; width:15px; height:15px; background:{color}; margin-right:3px; border:1px solid #ccc;" title="{color}"></span>'
            return format_html(badges)
        return "—"
    display_colors.short_description = "Colors"

    def discount_badge(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="color:white; background:red; padding:2px 5px; border-radius:3px;">-{}%</span>',
                int(obj.discount_percentage)
            )
        return "—"
    discount_badge.short_description = "Discount"

    def is_new_badge(self, obj):
        if obj.is_new:
            return format_html(
                '<span style="color:white; background:green; padding:2px 5px; border-radius:3px;">NEW</span>'
            )
        return "—"
    is_new_badge.short_description = "New Product"

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    ordering = ('-created_at',)
