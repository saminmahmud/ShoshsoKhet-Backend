from datetime import datetime
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from accounts.models import BuyerProfile, SellerProfile

class PlatformCommission(models.Model):
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=8.00,
        help_text="Commission percentage (e.g., 8.00 for 8%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Platform Commission: {self.commission_rate}%"
    
    @classmethod
    def get_platform_commission(cls):
        object, created = cls.objects.get_or_create(id=1)
        return object.commission_rate
    
    
    
class PlatformRevenue(models.Model):
    REVENUE_TYPE_CHOICES = (
        ('commission', 'Order Commission'),
        ('advertisement', 'Advertisement'),
    )

    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPE_CHOICES)
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, null=True, blank=True, related_name='revenues')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, null=True, blank=True)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.revenue_type} - ${self.amount} on {self.created_at.strftime('%Y-%m-%d')}"
    
    @classmethod
    def get_total_revenue(cls, start_date=None, end_date=None):
        """Get total revenue within date range"""
        queryset = cls.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        total = queryset.aggregate(total=models.Sum('amount'))['total']
        return total or Decimal('0.00')
    
    @classmethod
    def get_monthly_revenue(cls, year=None, month=None):
        """Get revenue for specific month"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        total = cls.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=models.Sum('amount'))['total']
        
        return total or Decimal('0.00')
    
    class Meta:
        indexes = [
            models.Index(fields=['revenue_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['seller']),
            models.Index(fields=['buyer']),
        ]


