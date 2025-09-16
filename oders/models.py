from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from products.models import Product
from coupons.models import Coupon  # ✅ Link to Coupon model

# ------------------------------------------------------
# Order Model
# ------------------------------------------------------
class Order(models.Model):
    """
    Represents a customer's order.
    Includes:
    - Status tracking
    - Delivery details
    - Coupon integration
    - Auto-calculation for discounted totals
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Customer who placed the order",
    )
    full_name = models.CharField(max_length=150, help_text="Receiver's full name")
    address = models.TextField(help_text="Delivery address")
    city = models.CharField(max_length=100, help_text="City for delivery")
    pin_code = models.CharField(max_length=10, help_text="Postal or ZIP code")
    phone = models.CharField(max_length=20, help_text="Contact phone number")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Order status",
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total cost before discounts",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
        help_text="Applied coupon, if any",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount amount applied from the coupon",
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final payable amount after discounts",
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Order creation date")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated date")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Order #{self.id} by {self.customer.email}"

    def apply_coupon(self):
        """
        Recalculate discount and final price based on the coupon.
        """
        if self.coupon and self.coupon.is_valid(order_total=self.total_price):
            discounted_total = self.coupon.apply_discount(self.total_price)
            self.discount_amount = self.total_price - discounted_total
            self.final_price = discounted_total
        else:
            self.discount_amount = 0
            self.final_price = self.total_price

    def save(self, *args, **kwargs):
        """
        Override save to ensure coupon logic is applied before saving.
        """
        self.apply_coupon()
        super().save(*args, **kwargs)


# ------------------------------------------------------
# Order Item Model
# ------------------------------------------------------
class OrderItem(models.Model):
    """
    Represents individual products in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The order this item belongs to",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        help_text="The product being purchased",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of this product",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price at the time of purchase",
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        indexes = [models.Index(fields=["order", "product"])]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        """Calculate subtotal for this item safely."""
        price = self.price or 0
        quantity = self.quantity or 0
        return price * quantity



# ------------------------------------------------------
# Payment Model
# ------------------------------------------------------
class Payment(models.Model):
    """
    Stores payment details for an order.
    """
    PAYMENT_METHODS = [
        ("cod", "Cash on Delivery"),
        ("card", "Credit/Debit Card"),
        ("upi", "UPI"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        help_text="Associated order for this payment",
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, help_text="Payment method used")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount paid")
    paid_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of payment")
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional transaction ID for online payments",
    )

    class Meta:
        ordering = ["-paid_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment for Order #{self.order.id} ({self.method})"
