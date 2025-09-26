from django.db import models
from products.models import Category  # import your existing Category model

class FastBanner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="banners/fast/")
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.URLField(blank=True, null=True)
    discount_text = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="fast_banners"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fast Banner"
        verbose_name_plural = "Fast Banners"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SecondBanner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="banners/second/")
    button_text = models.CharField(max_length=50, blank=True, null=True)
    button_url = models.URLField(blank=True, null=True)
    discount_text = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="second_banners"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Second Banner"
        verbose_name_plural = "Second Banners"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
