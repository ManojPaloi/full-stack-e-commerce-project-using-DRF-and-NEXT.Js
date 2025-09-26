from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    button = models.CharField(max_length=100, blank=True, null=True)
    discount_text = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
