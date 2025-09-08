# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import CustomUser, EmailOTP
import json

User = get_user_model()


# -------------------------------------------------------------------
# User Serializer
# -------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for full user details.
    Ensures sensitive fields (password) are write-only.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "groups": {"read_only": True},
            "user_permissions": {"read_only": True},
        }


# -------------------------------------------------------------------
# Register Serializer
# -------------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Includes `password2` for confirmation before creating a new user.
    """

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = [
            "first_name", "last_name", "email", "mobile_no",
            "address", "pin_code", "password", "password2"
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)  # remove confirmation field
        user = CustomUser.objects.create_user(
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data["email"],
            mobile_no=validated_data.get("mobile_no", ""),
            address=validated_data.get("address", ""),
            pin_code=validated_data.get("pin_code", ""),
            password=validated_data["password"],
            is_active=False,  # user must verify OTP
        )
        return user


# -------------------------------------------------------------------
# Login Serializer
# -------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts either email or username in `login` field.
    """
    login = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        login = data.get("login")
        password = data.get("password")

        if not login or not password:
            raise serializers.ValidationError(
                {"detail": "Both login (email/username) and password are required."}
            )

        # Try finding the user (by email or username)
        user_qs = User.objects.filter(
            email__iexact=login if "@" in login else None,
            username__iexact=login if "@" not in login else None
        ).distinct()

        if not user_qs.exists():
            raise serializers.ValidationError(
                {"detail": "Invalid email/username or password."}
            )

        user = user_qs.first()

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Invalid email/username or password."}
            )

        # Check if active
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "Your account is not active. Please verify your email before login."}
            )

        data["user"] = user
        return data
# -------------------------------------------------------------------
# Profile Update Serializer
# -------------------------------------------------------------------
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Username cannot be modified once created.
    """

    username = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "mobile_no",
            "address",
            "pin_code",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# -------------------------------------------------------------------
# OTP Serializer
# -------------------------------------------------------------------
class EmailOTPSerializer(serializers.ModelSerializer):
    """
    Serializer for validating OTPs for multiple purposes:
    - Registration
    - Password Reset
    - Login OTP
    """

    email = serializers.EmailField(write_only=True)
    code = serializers.CharField(write_only=True, max_length=6)
    purpose = serializers.CharField(write_only=True)

    class Meta:
        model = EmailOTP
        fields = ["email", "code", "purpose"]

    def validate(self, data):
        email = data.get("email")
        code = data.get("code")
        purpose = data.get("purpose")

        try:
            otp = EmailOTP.objects.filter(
                email=email, purpose=purpose, is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("No valid OTP found for this email. Please request a new one.")

        if otp.is_expired():
            raise serializers.ValidationError("The OTP has expired. Please request a new one.")

        if otp.code != code:
            raise serializers.ValidationError("Invalid OTP. Please check and try again.")

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # ✅ If for registration, create user
        if purpose == "registration":
            try:
                pending_data = json.loads(otp.extra_data or "{}")
            except Exception:
                raise serializers.ValidationError("Registration data is corrupted or missing.")

            if not pending_data:
                raise serializers.ValidationError("No registration data found with this OTP.")

            password = pending_data.pop("password")
            user = CustomUser.objects.create_user(
                password=password, **pending_data
            )
            user.is_active = True
            user.save()
            data["user"] = user

        else:
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("User not found for this email.")
            data["user"] = user

        return data


# -------------------------------------------------------------------
# Password Reset Serializer
# -------------------------------------------------------------------
class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting password after OTP verification.
    Ensures both password fields match before updating.
    """

    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "No account found with this email."})

        data["user"] = user
        data["new_password"] = password
        return data


# -------------------------------------------------------------------
# Verify OTP Serializer (lightweight)
# -------------------------------------------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    """
    Simple OTP verification serializer.
    Used for quick checks (not tied to registration).
    """

    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField(default="registration")
