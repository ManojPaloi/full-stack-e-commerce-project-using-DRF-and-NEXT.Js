"""
accounts/models.py

This module defines all database models for the accounts app:
- PendingUser: Temporary storage before OTP verification
- CustomUser: Main user model with email as the primary login field
- EmailOTP: Handles OTP generation/validation for registration, login, and password reset
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
    """
    Default expiry time for OTPs.

    Returns:
        datetime: Current time + 10 minutes
    """
    return timezone.now() + timedelta(minutes=10)


def generate_random_username(first_name: str = None) -> str:
    """
    Generate a unique, professional-looking random username.

    - With first name: john_4827, john.9283, johnx42
    - Without first name: user_8ab2, member_7gk1

    Args:
        first_name (str, optional): The first name of the user, used as prefix.

    Returns:
        str: A unique username (checked against CustomUser).
    """
    import random, string
    from .models import CustomUser  # local import to avoid circular issues

    base = first_name.lower() if first_name else random.choice(["user", "member", "guest"])

    while True:
        styles = [
            f"{base}_{random.randint(1000, 9999)}", 
            f"{base}.{random.randint(1000, 9999)}",
            f"{base}{random.choice(string.ascii_lowercase)}{random.randint(10, 99)}",
            f"{base}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=4))}",
        ]

        username = random.choice(styles)

        # ✅ Ensure uniqueness
        if not CustomUser.objects.filter(username=username).exists():
            return username


# -------------------------------------------------------------------
# Pending User (before OTP verification)
# -------------------------------------------------------------------

class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    mobile_no = models.CharField(max_length=15, unique=True, null=True, blank=True)  # ✅ Added field
    address = models.CharField(max_length=255, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)
    password = models.CharField(max_length=128)  # Already hashed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PendingUser: {self.email}"



# -------------------------------------------------------------------
# User Manager
# -------------------------------------------------------------------

class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model.
    Handles creation of normal users and superusers.
    """

    def create_user(self, email, password=None, first_name=None, mobile_no=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        email = self.normalize_email(email)

        # Ensure unique username
        if not extra_fields.get("username"):
            proposed_username = generate_random_username(first_name)
            while CustomUser.objects.filter(username=proposed_username).exists():
                proposed_username = generate_random_username(first_name)
            extra_fields["username"] = proposed_username

        # Respect is_active if provided; default to False
        is_active = extra_fields.pop("is_active", False)

        user = self.model(
            email=email,
            first_name=first_name or "",
            mobile_no=mobile_no,
            **extra_fields,
        )
        user.set_password(password)
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        # Ensure username exists
        if not extra_fields.get("username"):
            extra_fields["username"] = generate_random_username("admin")  # default for superuser

        return self.create_user(email, password=password, **extra_fields)


# -------------------------------------------------------------------
# User Model
# -------------------------------------------------------------------

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where email is the primary identifier for authentication.
    Includes additional fields like mobile_no, address, and pin_code.
    """
    profile_pic = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
        default=None,
        help_text="Optional profile picture for the user."
    )
    username   = models.CharField(max_length=50, unique=True, editable=False)
    email      = models.EmailField(unique=True, null=False, blank=False)
    mobile_no  = models.CharField(max_length=10, unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=30, blank=True)
    last_name  = models.CharField(max_length=30, blank=True)
    address    = models.TextField(blank=True, null=True)
    pin_code   = models.CharField(max_length=6, blank=True, null=True)

    is_staff   = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=False)  # Inactive until OTP verified

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        """Ensure username is auto-generated if not set."""
        if not self.username:
            proposed_username = generate_random_username(self.first_name)
            while CustomUser.objects.filter(username=proposed_username).exists():
                proposed_username = generate_random_username(self.first_name)
            self.username = proposed_username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email or self.username


# -------------------------------------------------------------------
# Email OTP Model
# -------------------------------------------------------------------

class EmailOTP(models.Model):
    """
    Model to store OTPs for user verification.

    Supports three main purposes:
    - registration
    - login
    - password reset
    """
    PURPOSE_CHOICES = [
        ("registration", "Registration"),
        ("login", "Login"),
        ("password_reset", "Password Reset"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
        null=True,   # OTP can exist before user is created
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
        indexes = [
            models.Index(fields=["email", "purpose", "is_used", "created_at"]),
        ]
        ordering = ["-created_at"]

    def is_expired(self):
        """
        Check if the OTP is expired.

        Returns:
            bool: True if expired, False otherwise
        """
        return timezone.now() >= self.expires_at

    @classmethod
    def create_new(cls, email: str, purpose: str = "registration", ttl_minutes: int = 10, user=None) -> "EmailOTP":
        """
        Generate and save a new OTP for the given email/purpose.

        Args:
            email (str): User email
            purpose (str): One of 'registration', 'login', or 'password_reset'
            ttl_minutes (int): Time-to-live in minutes
            user (CustomUser, optional): Related user instance

        Returns:
            EmailOTP: Newly created OTP object
        """
        code = ''.join(random.choices("0123456789", k=6))
        now = timezone.now()
        return cls.objects.create(
            user=user,
            email=email,
            code=code,
            purpose=purpose,
            expires_at=now + timedelta(minutes=ttl_minutes),
        )

    def mark_used(self):
        """Mark this OTP as used (cannot be reused)."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.code}"





class BlacklistedAccessToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)  # JWT ID
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blacklisted JTI: {self.jti}"