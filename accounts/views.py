"""
accounts/views.py
==================
This module implements:
- User registration with OTP verification (pending user storage until OTP is confirmed)
- Login with HttpOnly refresh cookie (SimpleJWT)
- Cookie-based refresh token rotation
- Logout (blacklisting refresh token + deleting cookie)
- Profile view/update
- Admin user listing
- Password reset flow using OTP
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.exceptions import InvalidToken
from django.db import IntegrityError
import random

# Local imports
from .models import CustomUser, EmailOTP, PendingUser
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    PasswordResetSerializer,
)

User = get_user_model()

# -------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------

def generate_otp() -> str:
    """Generate a random 6-digit OTP code."""
    return str(random.randint(100000, 999999))

def send_otp_email(email: str, otp_code: str, purpose="verification", user_name=None):
    """
    Sends OTP via email with plain text and HTML versions.
    """
    subject = "Your OTP Code" if purpose == "verification" else "Password Reset OTP"
    context = {"otp_code": otp_code, "user_name": user_name or "User", "site_name": "Django Auth System"}

    text_content = render_to_string("emails/otp_email.txt", context)
    html_content = render_to_string("emails/otp_email.html", context)

    email_message = EmailMultiAlternatives(subject, text_content, None, [email])
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------

class RegisterView(generics.GenericAPIView):
    """
    Create a PendingUser and send OTP.
    User is only saved to CustomUser after OTP verification.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pending_user = PendingUser.objects.create(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                mobile_no=serializer.validated_data.get("mobile_no", ""),
                profile_pic=request.FILES.get("profile_pic"),
            )
        except IntegrityError as e:
            return Response(
                {"status": "error", "message": f"Could not create pending user: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = EmailOTP.objects.create(
            email=pending_user.email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(pending_user.email, otp.code, "verification")

        return Response(
            {"status": "success", "message": "OTP sent successfully.", "email": pending_user.email},
            status=status.HTTP_201_CREATED,
        )

# -------------------------------------------------------------------
# Login
# -------------------------------------------------------------------

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response(
            {
                "status": "success",
                "message": "Login successful 🎉",
                "access": access,
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

        # ✅ Cookie settings
        secure_cookie = settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", not settings.DEBUG)
        samesite_cookie = settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax")
        max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())

        response.set_cookie(
            key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token"),
            value=str(refresh),
            httponly=True,
            secure=secure_cookie,
            samesite=samesite_cookie,
            max_age=max_age,
            path="/",
        )
        return response



class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token"))
        if not refresh_token:
            return Response({"detail": "No refresh token cookie found."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)
        return Response({"access": serializer.validated_data["access"]}, status=status.HTTP_200_OK)


# -------------------------------------------------------------------
# Logout
# -------------------------------------------------------------------

class LogoutView(APIView):
    """
    Blacklist the refresh token and clear the cookie.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cookie_name = settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token")
        response = Response({"status": "success", "message": "Logged out."})
        refresh_token = request.COOKIES.get(cookie_name)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        response.delete_cookie(cookie_name, path="/")
        return response

# -------------------------------------------------------------------
# Profile View / Update
# -------------------------------------------------------------------

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET → Retrieve profile
    PATCH/PUT → Update profile
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

# -------------------------------------------------------------------
# Admin-only: List Users
# -------------------------------------------------------------------

class UserListView(generics.ListAPIView):
    """Admin view to list all registered users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

# -------------------------------------------------------------------
# OTP Verification / Resend
# -------------------------------------------------------------------

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("otp")

        if not email or not code:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        otp = EmailOTP.objects.filter(email=email, code=code, purpose="registration", is_used=False).first()
        if not otp or otp.is_expired():
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP as used
        otp.mark_used()

        # Move PendingUser → CustomUser
        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"detail": "Pending user not found."}, status=status.HTTP_404_NOT_FOUND)

        user = CustomUser.objects.create_user(
            email=pending.email,
            password=pending.password,
            first_name=pending.first_name,
            mobile_no=pending.mobile_no,
            is_active=True,  # ✅ Activate now
        )

        # Delete PendingUser after migration
        pending.delete()

        # Issue tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "detail": "OTP verified successfully.",
            "access": str(access),
            "user": {"email": user.email, "username": user.username},
        })
        # Set refresh token cookie
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=True,       # Use HTTPS in production
            samesite="None",   # For cross-site requests
            max_age=7*24*60*60
        )
        return response
    
    
    
    
    
class ResendOTPView(APIView):
    """
    Resend OTP to pending or inactive accounts.
    """
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"status": "error", "message": "Email is required."}, status=400)

        # Check if OTP resend is allowed
        last_otp = EmailOTP.objects.filter(email=email, purpose="registration").order_by("-created_at").first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            wait = int(self.COOLDOWN_SECONDS - (timezone.now() - last_otp.created_at).total_seconds())
            return Response({"status": "error", "message": f"Wait {wait}s before requesting another OTP."}, status=429)

        EmailOTP.objects.filter(email=email, purpose="registration").delete()
        otp_code = generate_otp()
        EmailOTP.objects.create(
            email=email, code=otp_code, purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        send_otp_email(email, otp_code, "verification")
        return Response({"status": "success", "message": "OTP resent."}, status=200)

# -------------------------------------------------------------------
# Password Reset Flow (Send → Verify → Reset)
# -------------------------------------------------------------------

class SendPasswordResetOTPView(APIView):
    """Send OTP for password reset."""
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"status": "error", "message": "Email is required."}, status=400)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"status": "error", "message": "User not found."}, status=404)

        otp_code = generate_otp()
        EmailOTP.objects.create(
            user=user, email=email, code=otp_code, purpose="password_reset",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        send_otp_email(email, otp_code, "password_reset")
        return Response({"status": "success", "message": "OTP sent."}, status=200)

class VerifyPasswordResetOTPView(APIView):
    """Verify OTP for password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp")
        if not email or not otp_code:
            return Response({"status": "error", "message": "Email and OTP required."}, status=400)

        try:
            otp_obj = EmailOTP.objects.filter(email=email, code=otp_code, purpose="password_reset", is_used=False).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response({"status": "error", "message": "Invalid or expired OTP."}, status=400)

        if otp_obj.is_expired():
            return Response({"status": "error", "message": "OTP expired."}, status=400)

        otp_obj.is_used = True
        otp_obj.save()
        return Response({"status": "success", "message": "OTP verified."}, status=200)

class ResetPasswordView(APIView):
    """Set a new password after OTP verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        EmailOTP.objects.filter(email=user.email, purpose="password_reset").delete()
        return Response({"status": "success", "message": "Password reset successful."}, status=200)
