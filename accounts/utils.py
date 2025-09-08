import random
from django.core.mail import send_mail
import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError




logger = logging.getLogger(__name__)




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
    Custom exception handler:
    - Uses DRF's default exception handler for standard errors.
    - Logs unexpected errors.
    - Shows detailed errors in DEBUG mode, generic error in production.
    """
    # Call DRF default handler first
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Log unhandled exceptions
    logger.error("Unhandled exception: %s", str(exc), exc_info=True)

    # If DEBUG=True, show real error for easier debugging
    if settings.DEBUG:
        return Response(
            {
                "status": "error",
                "message": str(exc),   # show real error in dev
                "type": exc.__class__.__name__,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # In production, return safe generic error
    return Response(
        {
            "status": "error",
            "message": "Something went wrong. Please try again later.",
        },
        status=status.HTTP_400_BAD_REQUEST,
    )
