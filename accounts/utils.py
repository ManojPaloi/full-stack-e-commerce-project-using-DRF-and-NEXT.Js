import random
from django.core.mail import send_mail
from django.conf import settings

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
