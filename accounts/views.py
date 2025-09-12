from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import BlacklistedAccessToken
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # ❗ Prevent duplicate pending or registered users
        if PendingUser.objects.filter(email=email).exists():
            return Response({"detail": "Email already pending verification."},
                            status=status.HTTP_400_BAD_REQUEST)

        from accounts.models import CustomUser
        if CustomUser.objects.filter(email=email).exists():
            return Response({"detail": "Email already registered."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save data temporarily in PendingUser
        pending = PendingUser.objects.create(
            email=email,
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            address=serializer.validated_data.get("address", ""),
            pin_code=serializer.validated_data.get("pin_code", ""),
            password=serializer.validated_data["password"],  # hashed later
        )

        # Create OTP (no user yet)
        otp = EmailOTP.objects.create(
            email=pending.email,
            code=generate_otp(),
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

        send_otp_email(pending.email, otp.code, "verification")

        return Response({
            "status": "success",
            "message": "An OTP has been sent to your email. Verify to complete registration.",
            "email": pending.email,
        }, status=status.HTTP_201_CREATED)


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
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"status": "error", "message": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Blacklist refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Blacklist current access token too
            access_token = request.auth
            if access_token:
                jti = access_token.get("jti")
                if jti:
                    BlacklistedAccessToken.objects.get_or_create(jti=jti)

            return Response(
                {"status": "success", "message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"status": "success", "message": "Already logged out."},
                status=status.HTTP_200_OK,
            )
            
            


class CustomTokenRefreshView(TokenRefreshView):
    """
    Handles access token refresh.
    Automatically updates cookies if needed.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Set cookies for frontend
        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")

        if access_token:
            response.set_cookie(
                key="access",
                value=access_token,
                max_age=60,  # 1 minute
                httponly=True,
                samesite="Lax",
            )
        if refresh_token:
            response.set_cookie(
                key="refresh",
                value=refresh_token,
                max_age=24*60*60,  # 1 day
                httponly=True,
                samesite="Lax",
            )

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
    """Verify OTP, activate account, and migrate PendingUser → CustomUser."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        code = request.data.get("otp")

        if not email or not code:
            return Response(
                {"status": "error", "message": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Find OTP record
        try:
            otp_obj = EmailOTP.objects.filter(
                email=email, code=code, purpose="registration", is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            return Response(
                {"status": "error", "message": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Check expiry
        if otp_obj.is_expired():
            return Response(
                {"status": "error", "message": "OTP expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Mark OTP as used
        otp_obj.mark_used()

        # ✅ Fetch pending registration
        try:
            pending = PendingUser.objects.get(email=email)
        except PendingUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "No pending registration found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Create active CustomUser
        user = CustomUser.objects.create(
            email=pending.email,
            first_name=pending.first_name,
            last_name=pending.last_name,
            address=pending.address,
            pin_code=pending.pin_code,
            is_active=True
        )
        # Set password correctly (PendingUser.password is already hashed)
        user.password = pending.password  
        user.save()

        # ✅ Delete pending record
        pending.delete()

        return Response(
            {
                "status": "success",
                "title": "OTP Verified ✅",
                "message": "Account verified successfully.",
                "next_step": "Go to login and access your account.",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
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
