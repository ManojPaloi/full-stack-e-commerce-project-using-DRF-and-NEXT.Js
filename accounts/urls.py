from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,               # ✅ Add this import
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    LogoutView,
    ProfileView,
    UserListView,
    SendPasswordResetOTPView,
    VerifyPasswordResetOTPView,
    ResetPasswordView,
)

@api_view(["GET"])
def accounts_root(request, format=None):
    return Response({
        "register": request.build_absolute_uri("register/"),
        "otp": {
            "send": request.build_absolute_uri("otp/send/"),   # ✅ Add to root
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

urlpatterns = [
    # ✅ OTP for registration
    path("", accounts_root, name="accounts-root"),
    path("register/", RegisterView.as_view(), name="register"),      # ✅ Added send OTP endpoint
    path("otp/verify/", VerifyOTPView.as_view(), name="verify_otp"),
    path("otp/resend/", ResendOTPView.as_view(), name="resend_otp"),

    # ✅ Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("users/", UserListView.as_view(), name="users"),

    # ✅ Password Reset Flow
    path("password/forgot/", SendPasswordResetOTPView.as_view(), name="forgot_password"),
    path("password/verify-otp/", VerifyPasswordResetOTPView.as_view(), name="verify_password_otp"),
    path("password/reset/", ResetPasswordView.as_view(), name="reset_password"),

    # ✅ JWT Tokens
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]



