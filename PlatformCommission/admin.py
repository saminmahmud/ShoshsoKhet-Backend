from django.contrib import admin
from .models import PlatformCommission, PlatformRevenue

@admin.register(PlatformCommission)
class PlatformCommissionAdmin(admin.ModelAdmin):
    list_display = ('commission_rate', 'updated_at')
    readonly_fields = ('updated_at',)

@admin.register(PlatformRevenue)
class PlatformRevenueAdmin(admin.ModelAdmin):
    list_display = ('revenue_type', 'order', 'seller', 'buyer', 'amount', 'description', 'transaction_id', 'created_at')
    readonly_fields = ('created_at',)
