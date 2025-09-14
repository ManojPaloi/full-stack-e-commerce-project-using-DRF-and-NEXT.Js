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
from rest_framework.response import Response
from rest_framework import status

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

def send_otp_email(email, otp_code, purpose="verification", user_name=None):
    """
    Send an OTP email to the user using both text and HTML templates.
    """
    subject = "Your OTP Code" if purpose == "verification" else "Password Reset OTP"

    context = {
        "otp_code": otp_code,
        "user_name": user_name or "User",
        "site_name": "Django Auth System",
    }

    # Load text and HTML templates
    text_content = render_to_string("emails/otp_email.txt", context)
    html_content = render_to_string("emails/otp_email.html", context)

    # Create email with both text and HTML parts
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
        to=[email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send()

# ------------------------
# Authentication & User Management
# ------------------------
from django.db import IntegrityError

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Try to save user data temporarily in PendingUser
            pending_user = PendingUser.objects.create(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],  # Hash later after OTP verification
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                mobile_no=serializer.validated_data.get("mobile_no", ""),
                profile_pic=request.FILES.get("profile_pic"),
            )
        except IntegrityError as e:
            # Handle duplicate or unique constraint violations
            return Response(
                {
                    "status": "error",
                    "message": f"Could not create pending user: {str(e)}. "
                               f"If you already registered with this email, please complete OTP verification or use a different email.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # Catch all other unexpected errors gracefully
            return Response(
                {
                    "status": "error",
                    "message": f"An unexpected error occurred during registration: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate OTP for this pending user
        otp = EmailOTP.objects.create(
            email=pending_user.email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

        # Send OTP email
        send_otp_email(pending_user.email, otp.code, "verification")

        return Response(
            {
                "status": "success",
                "message": "OTP sent successfully. Please verify your email to complete registration.",
                "email": pending_user.email,
            },
            status=status.HTTP_201_CREATED,
        )





# -------------------------
# Login View (Cookie JWT)
# -------------------------
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "status": "success",
            "message": "Login successful 🎉",
            "access": access_token,
            "user": UserSerializer(user, context={"request": request}).data
        }, status=200)

        # Set HttpOnly cookie for refresh token
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=False,  # True in production
            samesite="Lax",
            max_age=24*60*60  # 1 day
        )
        return response

# -------------------------
# Refresh Access Token View
# -------------------------
class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh access token using HttpOnly refresh token stored in cookie.
    """

    def get_serializer(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None or "refresh" not in data:
            # Inject refresh token from cookie
            refresh_token = self.request.COOKIES.get("refresh")
            kwargs["data"] = {"refresh": refresh_token} if refresh_token else {}
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Invalid or missing refresh token."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Rotate refresh token cookie if configured
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh",
            value=serializer.validated_data.get("refresh", request.COOKIES.get("refresh")),
            httponly=True,
            secure=False,  # True in production
            samesite="Lax",
            max_age=24*60*60
        )
        return response

# -------------------------
# Logout View (Cookie JWT)
# -------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")
        response = Response({"status": "success", "message": "Logged out successfully."})

        # Remove cookie
        response.delete_cookie("refresh")

        # Blacklist token
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        # Optionally blacklist access token too
        access_token = request.auth
        if access_token:
            jti = access_token.get("jti")
            if jti:
                BlacklistedAccessToken.objects.get_or_create(jti=jti)

        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    # GET request
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({
            "status": "success",
            "message": "Profile retrieved.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # PATCH / PUT request
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "message": "Profile updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """Admin view to list all registered users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


# ------------------------
# OTP Views
# ------------------------
class VerifyOTPView(APIView):
    """Verify OTP, create real user from PendingUser, activate, and log in."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code = request.data.get("otp")

        if not email or not code:
            return Response(
                {"status": "error", "message": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find OTP for this email
        try:
            otp_obj = EmailOTP.objects.filter(
                email=email, code=code, purpose="registration", is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid or expired OTP."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check expiration
        if otp_obj.is_expired():
            return Response(
                {"status": "error", "message": "OTP expired. Request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Get PendingUser
        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "No pending registration found for this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create actual CustomUser
        user = CustomUser.objects.create_user(
            email=pending.email,
            password=pending.password,  # already plain text, will be hashed by create_user
            first_name=pending.first_name,
            last_name=pending.last_name,
            mobile_no=pending.mobile_no,
            profile_pic=pending.profile_pic,
            is_active=True,
        )

        # Clean up PendingUser
        pending.delete()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response(
            {
                "status": "success",
                "title": "OTP Verified ✅",
                "message": "Account verified and logged in successfully.",
                "email": user.email,
                "access": access,
                "refresh": str(refresh),
                "user": UserSerializer(user, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )




class ResendOTPView(APIView):
    """Resend OTP for users who are not yet verified or pending registration."""
    permission_classes = [AllowAny]
    COOLDOWN_SECONDS = 60  # 1 minute cooldown

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"status": "error", "message": "Email is required."},
                status=400,
            )

        # ✅ First check CustomUser
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"status": "info", "message": "Your account is already verified. Please log in."},
                    status=200,
                )
            # If found but inactive, use its email for OTP
            target_email = user.email
        except User.DoesNotExist:
            # ✅ If not found, check PendingUser
            try:
                pending = PendingUser.objects.get(email=email)
                target_email = pending.email
            except PendingUser.DoesNotExist:
                return Response(
                    {"status": "error", "message": "No pending or existing account found with this email."},
                    status=404,
                )

        # Cooldown check
        last_otp = EmailOTP.objects.filter(email=target_email, purpose="registration").order_by("-created_at").first()
        if last_otp and (timezone.now() - last_otp.created_at).total_seconds() < self.COOLDOWN_SECONDS:
            wait_time = int(self.COOLDOWN_SECONDS - (timezone.now() - last_otp.created_at).total_seconds())
            return Response(
                {"status": "error", "message": f"Please wait {wait_time} seconds before requesting another OTP."},
                status=429,
            )

        # Delete old OTPs
        EmailOTP.objects.filter(email=target_email, purpose="registration").delete()

        # Generate new OTP
        otp_code = generate_otp()
        EmailOTP.objects.create(
            email=target_email,
            code=otp_code,
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

        send_otp_email(target_email, otp_code, "verification")

        return Response(
            {
                "status": "success",
                "title": "New OTP Sent 🔁",
                "message": "A new OTP has been sent to your email.",
                "next_step": "Check your inbox or spam folder for the OTP.",
                "email": target_email,
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
    """Verify OTP for password reset using only OTP and email."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp")  # Only OTP

        if not email or not otp_code:
            return Response(
                {"status": "error", "message": "Email and OTP are required."},
                status=400,
            )

        try:
            # Automatically filter for password_reset OTPs
            otp_obj = EmailOTP.objects.filter(
                email=email, code=otp_code, purpose="password_reset", is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid or expired OTP."}, 
                status=400
            )

        if otp_obj.is_expired():
            return Response(
                {"status": "error", "message": "OTP expired. Request a new one."}, 
                status=400
            )

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        user = otp_obj.user
        if not user:
            return Response(
                {"status": "error", "message": "No user associated with this OTP."}, 
                status=404
            )

        return Response(
            {
                "status": "success",
                "title": "OTP Verified ✅",
                "message": "Your OTP has been successfully verified. You may now reset your password securely.",
                "next_step": "Proceed to set a new password to regain access to your account.",
                "email": user.email,
            },
            status=200,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        # Remove all password-reset OTPs for security
        EmailOTP.objects.filter(email=user.email, purpose="password_reset").delete()

        return Response(
            {
                "status": "success",
                "title": "Password Reset Successful 🔑",
                "message": "Your password has been updated successfully.",
                "next_step": "You can now log in with your new password.",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

