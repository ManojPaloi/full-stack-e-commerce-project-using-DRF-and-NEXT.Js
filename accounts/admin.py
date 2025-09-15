from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone

from .models import CustomUser, EmailOTP, PendingUser, BlacklistedAccessToken

# -------------------------------------------------------------------
# Custom User Admin
# -------------------------------------------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id", "profile_image_tag", "email", "username",
        "first_name", "last_name", "mobile_no",
        "status_badge", "staff_badge", "superuser_badge",
        "created_at", "updated_at",
    )
    list_display_links = ("id", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "username", "first_name", "last_name", "mobile_no")
    ordering = ("-created_at",)
    readonly_fields = ("username", "created_at", "updated_at", "profile_image_tag")

    fieldsets = (
        ("Account Info", {"fields": ("email", "password", "username")}),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "mobile_no", "address", "pin_code", "profile_pic"),
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Important Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2",
                "first_name", "last_name", "mobile_no", "profile_pic",
            ),
        }),
    )

    # Thumbnail preview for profile picture
    def profile_image_tag(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;" />',
                obj.profile_pic.url,
            )
        return "-"
    profile_image_tag.short_description = "Profile Picture"

    # Status badges
    def status_badge(self, obj):
        badge_class = "success" if obj.is_active else "danger"
        text = "Active" if obj.is_active else "Inactive"
        return format_html(f'<span class="badge badge-{badge_class}">{text}</span>')
    status_badge.short_description = "Status"

    def staff_badge(self, obj):
        badge_class = "primary" if obj.is_staff else "secondary"
        text = "Staff" if obj.is_staff else "—"
        return format_html(f'<span class="badge badge-{badge_class}">{text}</span>')
    staff_badge.short_description = "Staff"

    def superuser_badge(self, obj):
        badge_class = "warning" if obj.is_superuser else "secondary"
        text = "Superuser" if obj.is_superuser else "—"
        return format_html(f'<span class="badge badge-{badge_class}">{text}</span>')
    superuser_badge.short_description = "Superuser"

    # Optimize queries
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related("groups", "user_permissions")

# -------------------------------------------------------------------
# Email OTP Admin
# -------------------------------------------------------------------
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = (
        "id", "email", "purpose", "code",
        "created_at", "expires_at", "status_badge",
    )
    list_filter = ("purpose", "is_used", "created_at", "expires_at")
    search_fields = ("email", "code")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "expires_at")

    def status_badge(self, obj):
        if obj.is_used:
            badge_class = "secondary"
            text = "Used"
        elif obj.is_expired():
            badge_class = "danger"
            text = "Expired"
        else:
            badge_class = "success"
            text = "Valid"
        return format_html(f'<span class="badge badge-{badge_class}">{text}</span>')
    status_badge.short_description = "Status"

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

# -------------------------------------------------------------------
# Pending User Admin
# -------------------------------------------------------------------
@admin.register(PendingUser)
class PendingUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "mobile_no", "created_at")
    search_fields = ("email", "mobile_no")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

# -------------------------------------------------------------------
# Blacklisted Access Token Admin
# -------------------------------------------------------------------
@admin.register(BlacklistedAccessToken)
class BlacklistedAccessTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "jti", "blacklisted_at")
    search_fields = ("jti",)
    ordering = ("-blacklisted_at",)
