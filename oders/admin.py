from django.contrib import admin
from .models import Order, OrderItem, Payment

# ------------------------------------------------------
# Inline for Order Items
# ------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem inside Order.
    """
    model = OrderItem
    extra = 1
    readonly_fields = ("subtotal",)
    fields = ("product", "quantity", "price", "subtotal")

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Subtotal"


# ------------------------------------------------------
# Order Admin
# ------------------------------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for managing orders.
    """
    list_display = ("id", "customer", "status", "total_price", "created_at", "coupon_display")
    list_filter = ("status", "created_at")
    search_fields = ("id", "customer__email", "full_name", "phone")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Customer Info", {
            "fields": ("customer", "full_name", "phone", "address", "city", "pin_code"),
        }),
        ("Order Details", {
            "fields": ("status", "total_price", "coupon", "created_at", "updated_at"),
        }),
    )

    def coupon_display(self, obj):
        return obj.coupon.code if obj.coupon else "-"
    coupon_display.short_description = "Coupon"


# ------------------------------------------------------
# Order Item Admin
# ------------------------------------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for managing individual order items.
    """
    list_display = ("order", "product", "quantity", "price", "subtotal_display")
    search_fields = ("order__id", "product__name")
    list_filter = ("order__status",)

    def subtotal_display(self, obj):
        return obj.subtotal
    subtotal_display.short_description = "Subtotal"


# ------------------------------------------------------
# Payment Admin
# ------------------------------------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing payments.
    """
    list_display = ("order", "method", "amount", "paid_at", "transaction_id")
    search_fields = ("order__id", "transaction_id", "method")
    list_filter = ("method", "paid_at")
    date_hierarchy = "paid_at"
