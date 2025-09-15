"""
accounts/models.py

Defines:
- PendingUser: Temporary storage before OTP verification.
- CustomUser: Main user model with email as the primary login field.
- EmailOTP: Handles OTP generation/validation.
- BlacklistedAccessToken: Stores invalidated JWTs.
"""

import random
import string
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def otp_expiry_time():
    """Default expiry time for OTPs."""
    return timezone.now() + timedelta(minutes=10)


def generate_random_username(first_name: str = None) -> str:
    """
    Generate a unique username. Ensures no duplicates.
    """
    from .models import CustomUser
    base = first_name.lower() if first_name else random.choice(["user", "member", "guest"])
    while True:
        styles = [
            f"{base}_{random.randint(1000, 9999)}",
            f"{base}.{random.randint(1000, 9999)}",
            f"{base}{random.choice(string.ascii_lowercase)}{random.randint(10, 99)}",
            f"{base}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=4))}",
        ]
        username = random.choice(styles)
        if not CustomUser.objects.filter(username=username).exists():
            return username

# -------------------------------------------------------------------
# Pending User
# -------------------------------------------------------------------
class PendingUser(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_pic = models.ImageField(upload_to="pending_profiles/", blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Pending Users"

    def __str__(self):
        return f"PendingUser: {self.email}"

# -------------------------------------------------------------------
# Custom User Manager
# -------------------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, mobile_no=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        email = self.normalize_email(email)
        if not extra_fields.get("username"):
            extra_fields["username"] = generate_random_username(first_name)

        user = self.model(
            email=email,
            first_name=first_name or "",
            mobile_no=mobile_no,
            **extra_fields,
        )
        user.set_password(password)
        user.is_active = extra_fields.get("is_active", False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password=password, **extra_fields)

# -------------------------------------------------------------------
# Custom User
# -------------------------------------------------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True, default=None)
    username = models.CharField(max_length=50, unique=True, editable=False)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=10, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = generate_random_username(self.first_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username

# -------------------------------------------------------------------
# Email OTP
# -------------------------------------------------------------------
class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("registration", "Registration"),
        ("login", "Login"),
        ("password_reset", "Password Reset"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,
        blank=True,
    )
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="registration")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=otp_expiry_time)
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["email", "purpose", "is_used", "created_at"])]
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def create_new(cls, email, purpose="registration", ttl_minutes=10, user=None):
        code = "".join(random.choices("0123456789", k=6))
        return cls.objects.create(
            user=user,
            email=email,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        )

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.code}"

# -------------------------------------------------------------------
# Blacklisted Tokens
# -------------------------------------------------------------------
class BlacklistedAccessToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted JTI: {self.jti}"
