"""
accounts/views.py
=================
Handles user authentication, OTP verification, password reset, and profile management
for the e-commerce API using Django REST Framework.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import BlacklistedAccessToken
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import random

from .models import CustomUser, EmailOTP, PendingUser
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    EmailOTPSerializer,
    PasswordResetSerializer,
)

User = get_user_model()

# ------------------------
# Utility Functions
# ------------------------
def generate_otp():
    """
    Generate a secure 6-digit One-Time Password (OTP).

    Returns:
        str: Random 6-digit number as a string.
    """
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp_code, purpose="verification", user_name=None):
    """
    Send an OTP email with both text and HTML content.

    Args:
        email (str): Recipient's email.
        otp_code (str): The 6-digit OTP.
        purpose (str): 'verification' or 'password_reset'.
        user_name (str): Optional name of the user.
    """
    subject = "Your OTP Code" if purpose == "verification" else "Password Reset OTP"
    context = {
        "otp_code": otp_code,
        "user_name": user_name or "User",
        "site_name": "Django Auth System",
    }
    text_content = render_to_string("emails/otp_email.txt", context)
    html_content = render_to_string("emails/otp_email.html", context)

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,
        to=[email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()


# ------------------------
# Authentication & User Management
# ------------------------
class RegisterView(generics.GenericAPIView):
    """
    Register a new user.
    Stores data temporarily in PendingUser and sends an OTP for verification.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pending_user = PendingUser.objects.create(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            mobile_no=serializer.validated_data.get("mobile_no", ""),
            profile_pic=request.FILES.get("profile_pic")
        )

        otp = EmailOTP.objects.create(
            email=pending_user.email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(pending_user.email, otp.code, "verification")

        return Response(
            {
                "status": "success",
                "message": "📧 OTP sent! Check your email (including spam) to complete registration.",
                "email": pending_user.email,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Authenticate a user and return JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "status": "success",
                "message": "🎉 Login successful! Welcome back.",
                "access": access_token,
                "refresh": str(refresh),
                "user": UserSerializer(user, context={"request": request}).data
            },
            status=200
        )


class LogoutView(APIView):
    """
    Log out the user by blacklisting their tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"status": "error", "message": "❗ Refresh token is required to log out."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            access_token = request.auth
            if access_token:
                jti = access_token.get("jti")
                if jti:
                    BlacklistedAccessToken.objects.get_or_create(jti=jti)

            return Response(
                {"status": "success", "message": "✅ Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "info", "message": "Token already invalid or logged out."},
                status=status.HTTP_200_OK,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(
            {"status": "success", "message": "Profile retrieved.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"status": "success", "message": "✅ Profile updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    """
    Admin-only: List all registered users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class VerifyOTPView(APIView):
    """
    Verify OTP for registration and activate the user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("otp")

        if not email or not code:
            return Response(
                {"error": "❗ Email and OTP are required. Double-check and try again."},
                status=400
            )
        try:
            otp = EmailOTP.objects.get(email=email, code=code, purpose="registration")
        except EmailOTP.DoesNotExist:
            return Response({"error": "❌ Invalid OTP. Please request a new code."}, status=400)

        if otp.expires_at < timezone.now():
            return Response({"error": "⌛ OTP expired. Please request a new one."}, status=400)

        pending_user = PendingUser.objects.get(email=email)
        user = CustomUser.objects.create_user(
            email=pending_user.email,
            password=pending_user.password,
            first_name=pending_user.first_name,
            last_name=pending_user.last_name,
            mobile_no=pending_user.mobile_no,
            profile_pic=pending_user.profile_pic
        )

        pending_user.delete()
        otp.delete()

        return Response(
            {"status": "success", "message": "🎉 Registration complete! Your account is now active."}
        )


class ResendOTPView(APIView):
    """
    Resend OTP for users who haven't completed verification yet.
    """
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Please provide your email to resend the OTP."},
                status=400,
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "No account found with that email."},
                status=404,
            )
        if user.is_active:
            return Response(
                {"status": "info", "message": "Your account is already verified. Please log in."},
                status=200,
            )
        last_otp = EmailOTP.objects.filter(email=email, purpose="registration").order_by("-created_at").first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            wait_time = int(self.COOLDOWN_SECONDS - (timezone.now() - last_otp.created_at).total_seconds())
            return Response(
                {"status": "error", "message": f"Too many requests. Please wait {wait_time}s."},
                status=429,
            )

        EmailOTP.objects.filter(email=email, purpose="registration").delete()
        otp_code = generate_otp()
        otp = EmailOTP.objects.create(
            user=user,
            email=email,
            code=otp_code,
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(email, otp_code, "verification")

        return Response(
            {
                "status": "success",
                "title": "New OTP Sent 🔁",
                "message": "A fresh OTP has been sent to your email. Check your inbox or spam.",
                "email": email,
            },
            status=200,
        )


class SendPasswordResetOTPView(APIView):
    """
    Send an OTP to the user's email for password reset.
    """
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"status": "error", "message": "Please provide your email."}, status=400)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"status": "error", "message": "User not found."}, status=404)

        last_otp = EmailOTP.objects.filter(user=user, purpose="password_reset").order_by("-created_at").first()
        if last_otp:
            elapsed = (timezone.now() - last_otp.created_at).total_seconds()
            if elapsed < self.COOLDOWN_SECONDS and request.data.get("force") != True:
                return Response(
                    {"status": "error", "message": f"Please wait {int(self.COOLDOWN_SECONDS - elapsed)}s before requesting another OTP."},
                    status=429,
                )

        otp_code = generate_otp()
        otp = EmailOTP.objects.create(
            user=user,
            email=email,
            code=otp_code,
            purpose="password_reset",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(email, otp_code, "password_reset")

        return Response(
            {
                "status": "success",
                "title": "Password Reset OTP Sent 📩",
                "message": "We’ve sent an OTP to your email to reset your password.",
                "email": email,
            },
            status=200,
        )


class VerifyPasswordResetOTPView(APIView):
    """
    Verify the OTP for password reset.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp")

        if not email or not otp_code:
            return Response(
                {"status": "error", "message": "Email and OTP are required for verification."},
                status=400,
            )
        try:
            otp_obj = EmailOTP.objects.filter(
                email=email, code=otp_code, purpose="password_reset", is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid or expired OTP. Please try again."},
                status=400,
            )
        if otp_obj.is_expired():
            return Response(
                {"status": "error", "message": "Your OTP has expired. Request a new one."},
                status=400,
            )
        otp_obj.is_used = True
        otp_obj.save()

        user = otp_obj.user
        if not user:
            return Response(
                {"status": "error", "message": "No user associated with this OTP."},
                status=404,
            )
        return Response(
            {
                "status": "success",
                "title": "OTP Verified ✅",
                "message": "OTP verified successfully. You may now reset your password.",
                "email": user.email,
            },
            status=200,
        )


class ResetPasswordView(APIView):
    """
    Reset a user's password after OTP verification.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()
        EmailOTP.objects.filter(email=user.email, purpose="password_reset").delete()

        return Response(
            {
                "status": "success",
                "title": "Password Reset Successful 🔑",
                "message": "Your password has been updated. You can now log in.",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )
