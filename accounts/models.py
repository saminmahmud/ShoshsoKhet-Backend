from cloudinary_storage.storage import MediaCloudinaryStorage
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django_resized import ResizedImageField
from accounts.managers import CustomUserManager
from django.utils.translation import gettext_lazy as _


# ============================================
# 1. CUSTOM USER MODEL (3 types: Admin, Seller, Buyer)
# ============================================

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('seller', 'Seller/Farmer'),
        ('buyer', 'Buyer/Customer'),
    )

    email = models.EmailField(_("email address"), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, unique=True)
    profile_image = ResizedImageField(size=[300, 300], upload_to='profiles/', null=True, blank=True, quality=75, storage=MediaCloudinaryStorage())
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


# ============================================
# 2. SELLER/FARMER PROFILE
# ============================================

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    nid_number = models.CharField(max_length=20, unique=True)
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    address_details = models.TextField()
    
    def __str__(self):
        return f"{self.user.username} - {self.user.user_type}"


# ============================================
# 3. BUYER/CUSTOMER PROFILE
# ============================================

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    nid_number = models.CharField(max_length=20, unique=True)
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    address_details = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.user.user_type}"
