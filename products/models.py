from django.db import models
from django.utils.text import slugify
from django.conf import settings  
from category.models import Category  # adjust import path if needed

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="Select category for this product"
    )
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional discounted price"
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    colors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of colors, e.g. ['black', 'yellow', 'gray']"
    )
    is_available = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False, help_text="Mark as new product")
    rating = models.FloatField(default=0.0, help_text="Average rating out of 5")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)










class Review(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(default=1)  # 1-5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐ by {self.user.username}"
