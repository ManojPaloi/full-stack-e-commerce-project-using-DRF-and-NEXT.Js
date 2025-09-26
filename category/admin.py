from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Item

# -----------------------------
# Category Admin
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'image_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)

    # Shortened description for list display
    def description_short(self, obj):
        return (obj.description[:50] + "...") if obj.description else "—"
    description_short.short_description = "Description"

    # Display image preview in list and form
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px; max-width:50px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Image"


# -----------------------------
# Item Admin
# -----------------------------
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'discount_text', 'button', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'discount_text', 'button')
    readonly_fields = ()

    # Optional: Preview first image in admin
    def first_image_preview(self, obj):
        if obj.images:
            return format_html('<img src="{}" style="max-height:50px; max-width:50px;" />', obj.images[0])
        return "—"
    first_image_preview.short_description = "First Image"
