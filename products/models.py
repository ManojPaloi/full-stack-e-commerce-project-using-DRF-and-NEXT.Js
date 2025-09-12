from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from category.models import Category  # Adjust import path if needed

# --------------------------------------
# Product Model
# --------------------------------------
class Product(models.Model):
    """
    Represents a product in the store.

    Modern Features:
    - Slug auto-generation for SEO-friendly URLs
    - JSONField for multiple colors
    - Validators for ratings and stock
    - Optional discount price
    - Delivery charge and free delivery support
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Select the category for this product"
    )
    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Product name"
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        help_text="SEO-friendly URL slug, auto-generated if blank"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the product"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base price"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional discounted price"
    )
    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00,
        help_text="Delivery charge for this product (default 50, can be changed)"
    )
    free_delivery = models.BooleanField(
        default=False,
        help_text="If checked, delivery is free and delivery charge is ignored"
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Available stock quantity"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Main product image"
    )
    colors = models.JSONField(
        default=list,
        blank=True,
        help_text="Available colors, e.g. ['black', 'yellow', 'gray']"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Toggle availability"
    )
    is_new = models.BooleanField(
        default=False,
        help_text="Mark as a new product"
    )
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average rating (0 to 5)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date of creation"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date of last update"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['name', 'slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Automatically generate slug if not provided and handle free delivery."""
        if not self.slug:
            self.slug = slugify(self.name)
        if self.free_delivery:
            self.delivery_charge = 0
        elif not self.delivery_charge:
            self.delivery_charge = 50
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        """Return discount percentage if discount_price is set."""
        if self.discount_price and self.discount_price < self.price:
            return round(100 - (self.discount_price / self.price * 100), 2)
        return 0

    @property
    def is_on_sale(self):
        """Return True if product has a valid discount."""
        return self.discount_price is not None and self.discount_price < self.price


# --------------------------------------
# Review Model
# --------------------------------------
class Review(models.Model):
    """
    Represents a review given by a user for a product.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The product being reviewed"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="User who wrote the review"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="Optional review comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date of creation"
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['product', 'user']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.user.username}"
