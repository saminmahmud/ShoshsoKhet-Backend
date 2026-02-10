from django.contrib import admin
from .models import User, SellerProfile, BuyerProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nid_number', 'division', 'district', 'upazila')
    search_fields = ('user__username', 'user__email', 'nid_number', 'division', 'district', 'upazila')
    ordering = ('-user__created_at',)

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nid_number', 'division', 'district', 'upazila')
    search_fields = ('user__username', 'user__email', 'nid_number', 'division', 'district', 'upazila')
    ordering = ('-user__created_at',)
