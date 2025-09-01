from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, EmailOTP


@receiver(post_save, sender=CustomUser)
def delete_otp_after_activation(sender, instance, **kwargs):
    """
    Auto-delete OTPs after user account is successfully activated.
    """
    if instance.is_active:
        EmailOTP.objects.filter(email=instance.email).delete()
