# accounts/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

# ------------------------
# OTP Utilities
# ------------------------
def generate_otp():
    """Generate a random 6-digit OTP code."""
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp, purpose="verification"):
    """
    Send an OTP email to the user.

    Args:
        user_email (str): Recipient email address
        otp (str): OTP code
        purpose (str): 'verification' or 'password_reset'
    """
    subject = "Your OTP Code"
    if purpose == "password_reset":
        subject = "Password Reset OTP"

    message = f"""
    Hello,

    Your OTP is: {otp}.
    It will expire in 10 minutes.

    Thank you,
    Django Auth System
    """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        # Log the error; in production you might use logging instead of print
        print("Email sending failed:", e)

# # ------------------------
# # Custom Exception Handler
# # ------------------------
# def custom_exception_handler(exc, context):
#     """
#     Override DRF exception handler to handle JWT token errors globally.

#     Returns status 402 for expired/invalid JWT tokens.
#     """
#     response = exception_handler(exc, context)

#     if isinstance(exc, (TokenError, InvalidToken)):
#         return Response(
#             {"status": "error", "message": "Access token expired or invalid."},
#             status=402,
#         )

#     return response
