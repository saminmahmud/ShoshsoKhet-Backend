from cloudinary_storage.storage import MediaCloudinaryStorage
from django.db import models
from django_resized import ResizedImageField

from accounts.models import SellerProfile

UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('ltr', 'Liter'),
        ('pcs', 'Pieces'),
        ('dozen', 'Dozen'),
        ('hali', 'Hali (4 pcs)'),
    )

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = ResizedImageField(size=[300, 300], upload_to='categories/', null=True, blank=True, quality=75, storage=MediaCloudinaryStorage())
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    available_quantity = models.DecimalField(max_digits=8, decimal_places=2)
    min_order_quantity = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    is_organic = models.BooleanField(default=False)
    harvest_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.seller.user.username}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = ResizedImageField(size=[800, 800], upload_to='products/', quality=75, storage=MediaCloudinaryStorage())
    
    def __str__(self):
        return f"Image for {self.product.name}"
