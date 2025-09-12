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
    Serializer for full user details including profile picture URL.
    """
    profile_pic = serializers.SerializerMethodField()

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

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        if obj.profile_pic and hasattr(obj.profile_pic, 'url'):
            return request.build_absolute_uri(obj.profile_pic.url) if request else obj.profile_pic.url
        return None



# -------------------------------------------------------------------
# Register Serializer
# -------------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, label="Confirm Password")
    profile_pic = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            "first_name", "last_name", "email", "mobile_no",
            "address", "pin_code", "password", "password2", "profile_pic"
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        profile_pic = validated_data.pop("profile_pic", None)
        user = CustomUser.objects.create_user(
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data["email"],
            mobile_no=validated_data.get("mobile_no", ""),
            address=validated_data.get("address", ""),
            pin_code=validated_data.get("pin_code", ""),
            password=validated_data["password"],
            is_active=False,
        )
        if profile_pic:
            user.profile_pic = profile_pic
            user.save()
        return user


# -------------------------------------------------------------------
# Login Serializer
# -------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    """
    Login serializer supporting email or username.
    """
    login = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        login_input = data.get("login", "").strip()
        password = data.get("password")

        if not login_input or not password:
            raise serializers.ValidationError("Both login and password are required.")

        # Try to get user by email or username
        user = None
        if "@" in login_input:
            user = User.objects.filter(email__iexact=login_input).first()
        else:
            user = User.objects.filter(username__iexact=login_input).first()

        if not user:
            raise serializers.ValidationError("No account found with this email/username.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is not verified. Please check your email.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        data["user"] = user
        return data


# -------------------------------------------------------------------
# Profile Update Serializer
# -------------------------------------------------------------------
class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile, now including profile picture.
    """
    username = serializers.CharField(read_only=True)
    profile_pic = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "mobile_no",
            "address",
            "pin_code",
            "profile_pic",
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
    purpose = serializers.CharField(write_only=True, required=False, default="password_reset")

    class Meta:
        model = EmailOTP
        fields = ["email", "code", "purpose"]

    def validate(self, data):
        email = data.get("email")
        code = data.get("code")
        purpose = data.get("purpose") or "password_reset"  # default if not provided

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

        # Handle registration OTP
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
