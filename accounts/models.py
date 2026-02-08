# models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ============================================
# 1. CUSTOM USER MODEL (3 types: Admin, Seller, Buyer)
# ============================================

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('seller', 'Seller/Farmer'),
        ('buyer', 'Buyer/Customer'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, unique=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


# ============================================
# 2. SELLER/FARMER PROFILE
# ============================================

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    farm_name = models.CharField(max_length=200, null=True, blank=True)
    nid_number = models.CharField(max_length=20, unique=True)
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    village = models.CharField(max_length=100)
    address_details = models.TextField()
    is_approved = models.BooleanField(default=False)  # Admin approval
    
    def __str__(self):
        return f"{self.user.username} - {self.farm_name or 'Farmer'}"


# ============================================
# 3. BUYER/CUSTOMER PROFILE
# ============================================

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    division = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    upazila = models.CharField(max_length=50)
    address_details = models.TextField()

    def __str__(self):
        return f"{self.user.username} - Buyer"
