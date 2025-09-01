from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import CustomUser, EmailOTP


# -------------------------------------------------------------------
# Custom User Admin
# -------------------------------------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Enhanced Admin panel configuration for CustomUser with better UX"""

    list_display = (
        "id", "email", "username", "first_name", "last_name",
        "mobile_no", "status_badge", "staff_badge", "superuser_badge",
        "created_at", "updated_at",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "username", "first_name", "last_name", "mobile_no")
    ordering = ("-created_at",)

    readonly_fields = ("username", "created_at", "updated_at")

    fieldsets = (
        ("🔐 Account Info", {
            "fields": ("email", "password", "username"),
            "description": "Basic login information (username is auto-generated)."
        }),
        ("👤 Personal Info", {
            "fields": ("first_name", "last_name", "mobile_no", "address", "pin_code"),
            "description": "Optional details about the user."
        }),
        ("⚙️ Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "description": "Control user access and roles."
        }),
        ("⏱ Important Dates", {
            "fields": ("last_login", "created_at", "updated_at"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "mobile_no"),
        }),
    )

    # Custom colored badges
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✔ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✖ Inactive</span>')
    status_badge.short_description = "Active Status"

    def staff_badge(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            "blue" if obj.is_staff else "gray",
            "✔ Staff" if obj.is_staff else "—"
        )
    staff_badge.short_description = "Staff"

    def superuser_badge(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            "purple" if obj.is_superuser else "gray",
            "✔ Superuser" if obj.is_superuser else "—"
        )
    superuser_badge.short_description = "Superuser"


# -------------------------------------------------------------------
# Email OTP Admin
# -------------------------------------------------------------------
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Enhanced Admin panel configuration for OTP management"""

    list_display = (
        "id", "email", "purpose", "code",
        "created_at", "expires_at", "status_badge",
    )
    list_filter = ("purpose", "is_used", "created_at", "expires_at")
    search_fields = ("email", "code")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "expires_at")

    # Custom status with colors
    def status_badge(self, obj):
        if obj.is_used:
            return format_html('<span style="color: gray; font-weight: bold;">✔ Used</span>')
        elif obj.is_expired():
            return format_html('<span style="color: red; font-weight: bold;">✖ Expired</span>')
        return format_html('<span style="color: green; font-weight: bold;">✔ Valid</span>')
    status_badge.short_description = "Status"

    # Admin Actions
    actions = ["mark_selected_as_used", "delete_expired_otps"]

    def mark_selected_as_used(self, request, queryset):
        updated = queryset.update(is_used=True)
        self.message_user(request, f"{updated} OTP(s) marked as used.")
    mark_selected_as_used.short_description = "Mark selected OTPs as Used"

    def delete_expired_otps(self, request, queryset):
        expired_qs = queryset.filter(expires_at__lt=timezone.now(), is_used=False)
        count = expired_qs.count()
        expired_qs.delete()
        self.message_user(request, f"{count} expired OTP(s) deleted.")
    delete_expired_otps.short_description = "Delete expired OTPs"
