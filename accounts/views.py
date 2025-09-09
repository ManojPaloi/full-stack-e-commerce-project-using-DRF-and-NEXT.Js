from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
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
    """Generate a random 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp_code, purpose="verification"):
    """
    Send an OTP email to the user.

    Args:
        email (str): Recipient email address.
        otp_code (str): OTP code to send.
        purpose (str): Purpose of the OTP (verification/password_reset).
    """
    subject = "Your OTP Code"
    if purpose == "password_reset":
        subject = "Password Reset OTP"

    message = f"""
    Hello,

    Your OTP is {otp_code}.
    It will expire in 10 minutes.

    Thank you,
    Django Auth System
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
        recipient_list=[email],
        fail_silently=False,
    )


# ------------------------
# Authentication & User Management
# ------------------------
class RegisterView(generics.CreateAPIView):
    """Handle user registration with OTP email verification."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Register a new user:
        - Save user as inactive.
        - Generate OTP and send to email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)

        otp = EmailOTP.objects.create(
            user=user,
            email=user.email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

        send_otp_email(user.email, otp.code, "verification")

        return Response(
            {
                "status": "success",
                "title": "Registration Successful 🎉",
                "message": "An OTP has been sent to your email. Please verify your account.",
                "next_step": "Check your inbox or spam folder for the OTP.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )

# ------------------------
# Login View
# ------------------------
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response(
                {"status": "error", "message": "Please verify your email before login."},
                status=403,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": "success",
                "message": "Login successful 🎉",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=200,
        )


# ------------------------
# Logout View
# ------------------------
@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"status": "error", "message": "Refresh token required."},
                status=400,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"status": "success", "message": "Logout successful."},
                status=200,
            )
        except Exception:
            return Response(
                {"status": "error", "message": "Invalid or expired refresh token."},
                status=400,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update authenticated user profile."""
    serializer_class = ProfileUpdateSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(
            {"status": "success", "message": "Profile retrieved.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class UserListView(generics.ListAPIView):
    """Admin view to list all registered users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


# ------------------------
# OTP Views
# ------------------------
class SendOTPView(APIView):
    """Resend OTP for registration verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"status": "error", "message": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found."}, status=404)

        if user.is_active:
            return Response({"status": "info", "message": "Account already verified."}, status=200)

        last_otp = EmailOTP.objects.filter(user=user, purpose="registration").order_by("-created_at").first()
        if last_otp and (timezone.now() - last_otp.created_at).seconds < 60:
            return Response(
                {"status": "error", "message": "Please wait before requesting another OTP."},
                status=429,
            )

        otp_code = generate_otp()
        EmailOTP.objects.create(
            user=user,
            email=email,
            code=otp_code,
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        send_otp_email(email, otp_code, "verification")

        return Response({"status": "success", "message": "OTP sent to email."}, status=200)


class VerifyOTPView(APIView):
    """Verify OTP and activate user account."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code = request.data.get("otp")

        if not email or not code:
            return Response(
                {"status": "error", "message": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            otp_obj = EmailOTP.objects.filter(
                email=email, code=code, purpose="registration", is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response({"status": "error", "message": "Invalid or expired OTP."}, status=400)

        if otp_obj.is_expired():
            return Response({"status": "error", "message": "OTP expired. Request a new one."}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        user = otp_obj.user
        user.is_active = True
        user.save()

        return Response(
            {"status": "success",
        "title": "OTP Verified ✅",
        "message": "Account verified successfully.",
        "next_step": "Go to login and access your account.",
        "email": user.email,},
            status=200,
        )


class ResendOTPView(APIView):
    """Resend OTP for users who are not yet active."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Email is required."}, status=400
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "No account found with this email."},
                status=404,
            )

        # ✅ Check if user already verified
        if user.is_active:
            return Response(
                {
                    "status": "info",
                    "message": "Your account is already verified. Please login.",
                },
                status=200,
            )

        # Always delete old OTPs for this email
        EmailOTP.objects.filter(email=email, purpose="registration").delete()

        # Generate new OTP
        otp = EmailOTP.objects.create(
            user=user,
            email=email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

        # Send OTP email
        send_otp_email(email, otp.code, "verification")

        return Response(
            {
                "status": "success",
                "title": "New OTP Sent 🔁",
                "message": "A new OTP has been sent to your email.",
                "next_step": "Check your inbox or spam folder for the OTP.",
                "email": email,
            },
            status=200,
        )


# ------------------------
# Password Reset Flow
# ------------------------
class SendPasswordResetOTPView(APIView):
    """Send OTP for password reset request."""
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

        last_otp = EmailOTP.objects.filter(user=user, purpose="password_reset").order_by("-created_at").first()
        if last_otp:
            elapsed = (timezone.now() - last_otp.created_at).total_seconds()
            if elapsed < self.COOLDOWN_SECONDS and request.data.get("force") != True:
                return Response(
                    {"status": "error", "message": f"Please wait {int(self.COOLDOWN_SECONDS - elapsed)} seconds before requesting another OTP."},
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

        return Response({"status": "success",
    "title": "Password Reset OTP Sent 📩",
    "message": "An OTP has been sent to your email for password reset.",
    "next_step": "Check your inbox or spam folder for the OTP.",
    "email": "bilu@yopmail.com"},
          status=200)


class VerifyPasswordResetOTPView(APIView):
    """Verify OTP for password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        return Response(
            {"status": "success",
            "title": "OTP Verified ✅",
            "message": "Your OTP has been successfully verified. You may now reset your password securely.",
            "next_step": "Proceed to set a new password to regain access to your account.",
            "email": user.email,},
            status=200,
            )


class ResetPasswordView(APIView):
    """Reset user password after OTP verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        EmailOTP.objects.filter(email=user.email, purpose="password_reset").delete()

        return Response({"status": "success",
        "title": "Password Reset Successful 🔑",
        "message": "Your password has been updated successfully.",
        "next_step": "You can now log in with your new password.",
        "email": user.email,}, status=200)
