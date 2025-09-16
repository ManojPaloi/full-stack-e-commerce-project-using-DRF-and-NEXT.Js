from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Coupon(models.Model):
    """
    Represents a discount coupon for orders.
    Includes full validation, usage limits, and discount calculations.
    """

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),  # e.g., 10% off
        ("fixed", "Fixed Amount"),    # e.g., ₹500 off
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique code customers will use (e.g., SAVE10)."
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percentage",
        help_text="Select the type of discount."
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Value of the discount (e.g., 10 for 10% or ₹500 fixed)."
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Minimum order total required to apply this coupon."
    )
    valid_from = models.DateTimeField(help_text="Start date and time when this coupon becomes active.")
    valid_to = models.DateTimeField(help_text="Expiry date and time for this coupon.")
    active = models.BooleanField(default=True, help_text="Enable or disable this coupon globally.")
    usage_limit = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum times this coupon can be used (leave blank for unlimited)."
    )
    used_count = models.PositiveIntegerField(default=0, help_text="Number of times this coupon has been used.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date when this coupon was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date when this coupon was last updated.")

    class Meta:
        ordering = ["-valid_from"]
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["valid_from", "valid_to"]),
        ]

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percentage' else ''})"

    # -----------------------
    # Validation methods
    # -----------------------
    def is_valid(self, order_total=None):
        """
        Check if the coupon is valid for the current date and usage.
        Optionally checks minimum purchase requirement if order_total is provided.
        """
        now = timezone.now()

        if not self.active:
            return False
        if self.valid_from > now or self.valid_to < now:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        if order_total is not None and order_total < self.min_purchase_amount:
            return False
        return True

    def increment_usage(self):
        """
        Increment the used_count safely.
        """
        self.used_count += 1
        self.save(update_fields=["used_count"])

    # -----------------------
    # Discount application
    # -----------------------
    def apply_discount(self, total_amount):
        """
        Apply the discount to the given total amount and return the discounted total.
        """
        if not self.is_valid(order_total=total_amount):
            return total_amount

        if self.discount_type == "percentage":
            discount = (self.discount_value / 100) * total_amount
        else:
            discount = self.discount_value

        discounted_total = total_amount - discount
        return max(discounted_total, 0)  # Prevent negative totals

    @property
    def remaining_uses(self):
        """
        Returns the number of uses remaining or None if unlimited.
        """
        if self.usage_limit is None:
            return None
        return max(self.usage_limit - self.used_count, 0)

    @property
    def status(self):
        """
        Returns a human-readable status for admin or frontend.
        """
        if not self.active:
            return "Inactive"
        now = timezone.now()
        if self.valid_from > now:
            return "Not Started"
        if self.valid_to < now:
            return "Expired"
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return "Usage Limit Reached"
        return "Active"
