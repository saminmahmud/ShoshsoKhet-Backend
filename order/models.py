import uuid
from django.db import models
from PlatformCommission.models import PlatformCommission, PlatformRevenue
from accounts.models import BuyerProfile, SellerProfile
from product.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f"{self.order_id} - {self.buyer.user.username}"
    
    def calculate_total(self):
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.platform_commission = sum(item.commission_amount for item in items)
        self.total_amount = self.subtotal

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)

    def create_platform_revenue(self):
        PlatformRevenue.objects.create(
            revenue_type='commission',
            order=self,
            seller=None,
            buyer=self.buyer,
            amount=self.platform_commission,
            description=f"Commission from Order {self.order_id}",
            transaction_id=self.transaction_id
        )

    def reverse_platform_revenue(self):
        PlatformRevenue.objects.create(
            revenue_type='commission',
            order=self,
            seller=None,
            buyer=self.buyer,
            amount=-self.platform_commission,
            description=f"Reversal for Cancelled Order {self.order_id}",
            transaction_id=self.transaction_id
        )

    class Meta:
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['buyer']),
        ]
        ordering = ['-created_at']
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    seller_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price_per_unit
        self.commission_rate = PlatformCommission.get_platform_commission()
        self.commission_amount = self.calculate_commission()
        self.seller_payout = self.total_price - self.commission_amount
        super().save(*args, **kwargs)
    
    def calculate_commission(self):
        return (self.total_price * self.commission_rate / 100)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order {self.order.order_id}"
