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
    Custom exception handler for DRF.
    Returns 402 if JWT access token is expired or invalid.
    """
    if isinstance(exc, TokenError):
        return Response(
            {"status": "error", "message": "Access token expired or invalid."},
            status=402,
        )

    response = exception_handler(exc, context)
    return response