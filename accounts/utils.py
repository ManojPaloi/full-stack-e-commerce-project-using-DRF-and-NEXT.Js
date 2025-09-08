import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError

# -------------------------------------------------------------------
# OTP / Email Utilities
# -------------------------------------------------------------------
def generate_otp():
    """
    Generate a 6-digit OTP as a string.
    """
    return str(random.randint(100000, 999999))


def send_otp_email(user_email, otp):
    """
    Send an OTP email to the given user email.
    """
    subject = "Verify Your Email"
    message = f"Your OTP is: {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"[Email Error] Failed to send OTP to {user_email}: {e}")


# -------------------------------------------------------------------
# Custom DRF Exception Handler
# -------------------------------------------------------------------
def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Standardizes JWT/auth errors and permissions into consistent JSON responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # JWT / Authentication errors → 401
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated, TokenError, InvalidToken, TokenBackendError)):
        return Response(
            {"status": "error", "message": str(exc)},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Permission denied → 403
    if isinstance(exc, PermissionDenied):
        return Response(
            {"status": "error", "message": str(exc)},
            status=status.HTTP_403_FORBIDDEN
        )

    # If DRF default handler returned a response, standardize format
    if response is not None:
        response.data = {
            "status": "error",
            "message": response.data.get("detail", "Something went wrong.")
        }

    return response
