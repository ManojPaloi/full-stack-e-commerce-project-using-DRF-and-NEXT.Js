from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    RegisterView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    LogoutView,
    ProfileView,
    UserListView,
    SendPasswordResetOTPView,
    VerifyPasswordResetOTPView,
    ResetPasswordView,
    CookieTokenRefreshView,  # ✅ Custom refresh view
)

# -------------------------------------------------------------------
# 🌐 API Root Helper
# -------------------------------------------------------------------
@api_view(["GET"])
def accounts_root(request, format=None):
    """
    Lists available endpoints for quick navigation and debugging.
    """
    return Response({
        "register": request.build_absolute_uri("register/"),
        "otp": {
            "verify": request.build_absolute_uri("otp/verify/"),
            "resend": request.build_absolute_uri("otp/resend/"),
        },
        "login": request.build_absolute_uri("login/"),
        "logout": request.build_absolute_uri("logout/"),
        "profile": request.build_absolute_uri("profile/"),
        "users": request.build_absolute_uri("users/"),
        "password_reset": {
            "forgot": request.build_absolute_uri("password/forgot/"),
            "verify_otp": request.build_absolute_uri("password/verify-otp/"),
            "reset": request.build_absolute_uri("password/reset/"),
        },
        "jwt": {
            "token": request.build_absolute_uri("token/"),
            "refresh": request.build_absolute_uri("token/refresh/"),
        },
    })

# -------------------------------------------------------------------
# 🔗 URL Patterns
# -------------------------------------------------------------------
urlpatterns = [
    # 🌐 API root
    path("", accounts_root, name="accounts-root"),

    # 📝 Registration & OTP
    path("register/", RegisterView.as_view(), name="register"),
    path("otp/verify/", VerifyOTPView.as_view(), name="verify_otp"),
    path("otp/resend/", ResendOTPView.as_view(), name="resend_otp"),

    # 🔑 Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("users/", UserListView.as_view(), name="users"),

    # 🔐 Password Reset
    path("password/forgot/", SendPasswordResetOTPView.as_view(), name="forgot_password"),
    path("password/verify-otp/", VerifyPasswordResetOTPView.as_view(), name="verify_password_otp"),
    path("password/reset/", ResetPasswordView.as_view(), name="reset_password"),

    # 🔄 JWT Token Endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
]
