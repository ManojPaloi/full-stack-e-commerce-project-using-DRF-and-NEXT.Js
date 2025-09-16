from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from category.models import Category

class Product(models.Model):
    """
    Represents a product in the store.
    Includes:
    - Auto slug generation (unique)
    - Discount, delivery charge, colors, stock
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Select the category for this product"
    )
    name = models.CharField(max_length=150, unique=True, help_text="Product name")
    slug = models.SlugField(max_length=180, unique=True, blank=True, help_text="Auto-generated slug")
    description = models.TextField(blank=True, null=True, help_text="Product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price")
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, help_text="Optional discounted price"
    )
    delivery_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00, help_text="Delivery charge"
    )
    free_delivery = models.BooleanField(default=False, help_text="Free delivery?")
    stock = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0)], help_text="Available stock"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Product image")
    colors = models.JSONField(default=list, blank=True, help_text="Available colors")
    is_available = models.BooleanField(default=True, help_text="Available for sale?")
    is_new = models.BooleanField(default=False, help_text="Mark as new product")
    rating = models.FloatField(
        default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)], help_text="Average rating"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last updated")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [models.Index(fields=['name', 'slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Generate a unique slug from name if not set or name changed."""
        if not self.slug or slugify(self.name) != self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.free_delivery:
            self.delivery_charge = 0
        elif not self.delivery_charge or self.delivery_charge <= 0:
            self.delivery_charge = 50

        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.discount_price and self.discount_price < self.price:
            return round(100 - (self.discount_price / self.price * 100), 2)
        return 0

    @property
    def is_on_sale(self):
        return self.discount_price is not None and self.discount_price < self.price


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews', help_text="Reviewed product"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', help_text="Reviewer"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Rating (1–5)"
    )
    comment = models.TextField(blank=True, null=True, help_text="Review comment")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date created")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [models.Index(fields=['product', 'user'])]

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.user.username}"
