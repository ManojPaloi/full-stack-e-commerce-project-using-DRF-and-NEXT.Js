import random
from django.core.mail import send_mail
from django.conf import settings



from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp):
    subject = "Verify Your Email"
    message = f"Your OTP is: {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print("Email sending failed:", e)







def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize error responses.
    """
    # Call DRF's default handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Use DRF’s generated error details
        detail = response.data

        # Wrap into a consistent structure
        response.data = {
            "status": "error",
            "message": _get_error_message(detail),
            "errors": detail,  # full details (field errors, etc.)
        }
    else:
        # If response is None, it’s a server error (500, etc.)
        response = Response(
            {
                "status": "error",
                "message": "Internal server error. Please try again later.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_message(detail):
    """
    Extracts a user-friendly message from DRF's error detail.
    """
    if isinstance(detail, list):
        return " ".join([str(item) for item in detail])
    elif isinstance(detail, dict):
        # Pick the first field error
        first_key = next(iter(detail))
        return str(detail[first_key])
    return str(detail)