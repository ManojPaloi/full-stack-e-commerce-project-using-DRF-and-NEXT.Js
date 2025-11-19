"""
accounts/views.py
==================
This module implements the authentication and user management API endpoints, including:

- User registration with OTP verification (PendingUser storage until OTP confirmation)
- Login with HttpOnly refresh token cookie (SimpleJWT)
- Cookie-based refresh token rotation
- Logout with refresh token blacklisting and cookie deletion
- User profile retrieval and update
- Admin-only user listing
- Password reset flow using OTP (send → verify → reset)
"""

from typing import Optional
from threading import Thread
from datetime import timedelta 
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

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
# Utility Functions
# -------------------------------------------------------------------

def generate_otp() -> str:
    """
    Generate a 6-digit random OTP code.

    Returns:
        str: Random OTP code as string
    """
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp_code: str, purpose: str = "verification", user_name: Optional[str] = None):
    """
    Send OTP email to the user.

    Args:
        email (str): Recipient email address
        otp_code (str): OTP code to send
        purpose (str): "verification" or "password_reset"
        user_name (Optional[str]): User's name for personalized email
    """
    subject = "Your OTP Code" if purpose == "verification" else "Password Reset OTP"
    context = {
        "otp_code": otp_code,
        "user_name": user_name or "User",
        "site_name": "Django Auth System"
    }

    text_content = render_to_string("emails/otp_email.txt", context)
    html_content = render_to_string("emails/otp_email.html", context)

    email_message = EmailMultiAlternatives(subject, text_content, None, [email])
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


# Async email sending
def send_email_async(email, code):
    Thread(target=send_otp_email, args=(email, code, "verification")).start()



# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Password match validation
        if serializer.validated_data["password"] != serializer.validated_data["password2"]:
            return Response(
                {"status": "error", "message": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.contrib.auth.hashers import make_password
        password_hashed = make_password(serializer.validated_data["password"])
        email = serializer.validated_data["email"]

        # 🧹 Delete expired pending users and OTPs before creating new one
        EmailOTP.objects.filter(
            email=email,
            purpose="registration",
            expires_at__lt=timezone.now()
        ).delete()

        # If PendingUser exists but older than 10 min → delete it too
        existing_pending = PendingUser.objects.filter(email=email).first()
        if existing_pending:
            otp = EmailOTP.objects.filter(email=email, purpose="registration").order_by("-created_at").first()
            if not otp or otp.expires_at < timezone.now():
                existing_pending.delete()

        # Now safely create a new pending user
        try:
            pending_user, created = PendingUser.objects.get_or_create(
                email=email,
                defaults={
                    "password": password_hashed,
                    "first_name": serializer.validated_data.get("first_name", ""),
                    "last_name": serializer.validated_data.get("last_name", ""),
                    "mobile_no": serializer.validated_data.get("mobile_no", ""),
                    "profile_pic": request.FILES.get("profile_pic"),
                }
            )
        except IntegrityError as e:
            return Response(
                {"status": "error", "message": f"Could not create pending user: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not created:
            return Response(
                {"status": "error", "message": "Pending user already exists. Please verify OTP or wait before retrying."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new OTP (valid for 10 minutes)
        otp_code = generate_otp()
        EmailOTP.objects.create(
            email=pending_user.email,
            code=otp_code,
            purpose="registration",
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # Send OTP safely
        try:
            send_otp_email(pending_user.email, otp_code, "verification")
        except Exception as e:
            print("Email sending failed:", e)

        return Response(
            {"status": "success", "message": "OTP sent successfully.", "email": pending_user.email},
            status=status.HTTP_201_CREATED
        )



# -------------------------------------------------------------------
# Login
# -------------------------------------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Handle user login and set HttpOnly refresh token cookie.
    """
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

        # Cookie settings
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
    """
    Refresh access token using cookie-stored refresh token.
    """
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
    Logout user by blacklisting refresh token and deleting cookie.
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
    GET → Retrieve user profile.
    PATCH/PUT → Update user profile.
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
    """
    Admin view to list all registered users.
    """
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

        otp = EmailOTP.objects.filter(
            email=email, code=code,
            purpose="registration", is_used=False
        ).first()

        if not otp or otp.is_expired():
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp.mark_used()

        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response({"detail": "Pending user not found."}, status=status.HTTP_404_NOT_FOUND)

        # -----------------------------
        # ⭐ FIX: create user WITHOUT double hashing password
        # -----------------------------
        user = CustomUser.objects.create(
            email=pending.email,
            password=pending.password,   # already hashed
            first_name=pending.first_name,
            last_name=pending.last_name,
            mobile_no=pending.mobile_no,
            profile_pic=pending.profile_pic,
            is_active=True,
        )

        pending.delete()

        # -----------------------------
        # ⭐ Auto Login After OTP
        # -----------------------------
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response({
            "status": "success",
            "message": "OTP verified successfully. Logged in.",
            "access": access,
            "user": UserSerializer(user).data,
        })

        # set refresh cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT.get("AUTH_COOKIE", "refresh_token"),
            value=str(refresh),
            httponly=True,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "None"),
            max_age=7 * 24 * 60 * 60,
            path="/",
        )

        return response



class ResendOTPView(APIView):
    """
    Resend OTP to pending or inactive accounts with cooldown.
    """
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60  # 1-minute cooldown

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user recently requested an OTP
        last_otp = EmailOTP.objects.filter(
            email=email, purpose="registration"
        ).order_by("-created_at").first()

        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            wait = int(self.COOLDOWN_SECONDS - (timezone.now() - last_otp.created_at).total_seconds())
            return Response(
                {"status": "error", "message": f"Wait {wait}s before requesting another OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Delete old OTPs and create a new one
        EmailOTP.objects.filter(email=email, purpose="registration").delete()

        otp_code = generate_otp()
        EmailOTP.objects.create(
            email=email,
            code=otp_code,
            purpose="registration",
            expires_at=timezone.now() + timedelta(minutes=10)  # ✅ FIXED
        )

        send_otp_email(email, otp_code, "verification")
        return Response(
            {"status": "success", "message": "OTP resent successfully."},
            status=status.HTTP_200_OK
        )



# -------------------------------------------------------------------
# Password Reset Flow
# -------------------------------------------------------------------

class SendPasswordResetOTPView(APIView):
    """
    Send OTP for password reset with cooldown protection.
    """
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60  # 1-minute cooldown

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check cooldown
        last_otp = EmailOTP.objects.filter(
            email=email, purpose="password_reset"
        ).order_by("-created_at").first()

        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            wait = int(self.COOLDOWN_SECONDS - (timezone.now() - last_otp.created_at).total_seconds())
            return Response(
                {"status": "error", "message": f"Wait {wait}s before requesting another OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Create new OTP
        otp_code = generate_otp()
        EmailOTP.objects.create(
            user=user,
            email=email,
            code=otp_code,
            purpose="password_reset",
            expires_at=timezone.now() + timedelta(minutes=10)  # ✅ FIXED
        )

        send_otp_email(email, otp_code, "password_reset")
        return Response(
            {"status": "success", "message": "Password reset OTP sent."},
            status=status.HTTP_200_OK
        )



class VerifyPasswordResetOTPView(APIView):
    """
    Verify OTP for password reset.
    """
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
    """
    Reset password after OTP verification.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        EmailOTP.objects.filter(email=user.email, purpose="password_reset").delete()

        return Response({"status": "success", "message": "Password reset successful."}, status=200)
