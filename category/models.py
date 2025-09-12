from django.db import models




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    # New fields
    description = models.TextField(blank=True, null=True, help_text="Optional description for the category")
    image = models.ImageField(
        upload_to="categories/",  # folder inside MEDIA_ROOT where images will be stored
        blank=True,
        null=True,
        help_text="Upload an image for this category"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
