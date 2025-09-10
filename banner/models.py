from django.db import models

class FirstBanner(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Banner Title",
        help_text="Enter a catchy title for the first banner."
    )
    image = models.ImageField(
        upload_to="banners/first/",
        verbose_name="Banner Image",
        help_text="Upload an image for the first banner."
    )
    image_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Image Description",
        help_text="Optional: Provide a short description or alt text for accessibility."
    )
    link_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link URL",
        help_text="Optional: Add a URL to navigate when clicking the banner."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Uncheck to hide this banner on the site."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "First Banner"
        verbose_name_plural = "First Banners"
        ordering = ["-created_at"]

    def __str__(self):
        return f"First Banner - {self.title}"


class SecondBanner(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Banner Title",
        help_text="Enter a catchy title for the second banner."
    )
    image = models.ImageField(
        upload_to="banners/second/",
        verbose_name="Banner Image",
        help_text="Upload an image for the second banner."
    )
    image_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Image Description",
        help_text="Optional: Provide a short description or alt text for accessibility."
    )
    link_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link URL",
        help_text="Optional: Add a URL to navigate when clicking the banner."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Uncheck to hide this banner on the site."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Second Banner"
        verbose_name_plural = "Second Banners"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Second Banner - {self.title}"
