from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description_short', 'image_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')  # Filter by creation or update time
    search_fields = ('name', 'slug', 'description')  # Enable search
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug from name
    readonly_fields = ('image_preview',)  # Show image preview as read-only in form

    # Custom short description for the description field
    def description_short(self, obj):
        return (obj.description[:50] + "...") if obj.description else "—"
    description_short.short_description = "Description"

    # Display image preview in admin list and form
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "—"
    image_preview.allow_tags = True
    image_preview.short_description = "Image"
