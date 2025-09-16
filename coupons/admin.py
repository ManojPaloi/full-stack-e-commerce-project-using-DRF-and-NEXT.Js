from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "status", "active", "valid_from", "valid_to", "used_count")
    list_filter = ("active", "discount_type", "valid_from", "valid_to")
    search_fields = ("code",)
    ordering = ("-valid_from",)
