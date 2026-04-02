from decimal import Decimal
import uuid
from django.db import models
from django.utils import timezone
from PlatformCommission.models import PlatformCommission, PlatformRevenue
from accounts.models import BuyerProfile, SellerProfile
from product.models import Product

class EscrowAccount(models.Model):
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_held = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_released = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Escrow Account"
        verbose_name_plural = "Escrow Accounts"
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = f"ESC{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Escrow - Balance: {self.total_balance} TK"
    
    @classmethod
    def get_main_account(cls):
        account, created = cls.objects.get_or_create(id=1)
        return account



class EscrowTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('hold', 'Hold Payment'),
        ('release', 'Release to Seller'),
        ('refund', 'Refund to Buyer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    transaction_id = models.CharField(max_length=30, unique=True, editable=False)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='escrow_transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Gateway Info
    gateway_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Escrow Transaction"
        verbose_name_plural = "Escrow Transactions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"ESC{timezone.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} - {self.amount} TK"


class SellerWallet(models.Model):
    seller = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name='wallet')
    
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    last_withdrawal_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Seller Wallet"
        verbose_name_plural = "Seller Wallets"
    
    def __str__(self):
        return f"{self.seller.user.username} - Available: {self.available_balance} TK"
    
    def add_pending(self, amount):
        """Add to pending balance (escrow hold)"""
        self.pending_balance += Decimal(str(amount))
        self.save()
    
    def release_to_available(self, amount):
        """Release from pending to available (after delivery)"""
        amount = Decimal(str(amount))
        if self.pending_balance >= amount:
            self.pending_balance -= amount
            self.available_balance += amount
            self.total_earned += amount
            self.save()
            return True
        return False


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    ESCROW_STATUS_CHOICES = (
        ('pending', 'Payment Pending'),
        ('held', 'Payment Held in Escrow'),
        ('released', 'Payment Released to Sellers'),
        ('refunded', 'Payment Refunded to Buyer'),
    )
    
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE, related_name='orders')
    
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(null=True, blank=True)
    
    escrow_status = models.CharField(
        max_length=20, 
        choices=ESCROW_STATUS_CHOICES, 
        default='pending'
    )
    escrow_held_at = models.DateTimeField(null=True, blank=True)
    escrow_released_at = models.DateTimeField(null=True, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.order_id} - {self.buyer.user.username}"

    def calculate_total(self):
        if self.pk:
            items = self.items.all()
            new_subtotal = sum(item.total_price for item in items)
            new_commission = sum(item.commission_amount for item in items)

            Order.objects.filter(pk=self.pk).update(
                subtotal=new_subtotal,
                platform_commission=new_commission,
                total_amount=new_subtotal
            )
            self.subtotal = new_subtotal
            self.platform_commission = new_commission
            self.total_amount = new_subtotal

    def save(self, *args, **kwargs):
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

    def hold_payment_in_escrow(self):
        """
        Called after successful payment
        Holds payment in escrow account
        """
        if self.is_paid and self.escrow_status == 'pending':
            # Get escrow account
            escrow = EscrowAccount.get_main_account()
            
            # Hold payment
            escrow.total_held += self.total_amount
            escrow.total_balance += self.total_amount
            escrow.save()
            
            # Create escrow transaction
            EscrowTransaction.objects.create(
                order=self,
                transaction_type='hold',
                amount=self.total_amount,
                status='completed',
                gateway_transaction_id=self.transaction_id,
                notes=f"Payment held for order {self.order_id}",
                completed_at=timezone.now()
            )
            
            # Update order escrow status
            self.escrow_status = 'held'
            self.escrow_held_at = timezone.now()
            Order.objects.filter(pk=self.pk).update(
                escrow_status='held',
                escrow_held_at=timezone.now()
            )
            
            # Add to seller pending balance
            for item in self.items.all():
                wallet, created = SellerWallet.objects.get_or_create(
                    seller=item.product.seller
                )
                wallet.add_pending(item.seller_payout)
            
            return True
        return False
    
    def release_payment_to_sellers(self):
        """
        Called after delivery confirmation
        Releases payment from escrow to seller wallets
        """
        if self.escrow_status == 'held' and self.status == 'delivered':
            # Get escrow account
            escrow = EscrowAccount.get_main_account()
            
            for item in self.items.all():
                # Get seller wallet
                wallet, created = SellerWallet.objects.get_or_create(
                    seller=item.product.seller
                )
                
                # Release from pending to available
                wallet.release_to_available(item.seller_payout)
                
                # Create escrow transaction
                EscrowTransaction.objects.create(
                    order=self,
                    transaction_type='release',
                    amount=item.seller_payout,
                    status='completed',
                    notes=f"Payment released to {item.product.seller.user.username} for order {self.order_id}",
                    completed_at=timezone.now()
                )
                
                escrow.total_held -= item.seller_payout
                escrow.total_released += item.seller_payout
            
            # Platform commission stays with platform
            escrow.total_balance -= self.platform_commission
            escrow.save()
            
            # Update order escrow status
            self.escrow_status = 'released'
            self.escrow_released_at = timezone.now()
            Order.objects.filter(pk=self.pk).update(
                escrow_status='released',
                escrow_released_at=timezone.now()
            )
            
            return True
        return False
    
    def refund_to_buyer(self, reason=None):
        """
        Called when order is cancelled
        Refunds payment to buyer
        """
        if self.escrow_status == 'held':
            # Get escrow account
            escrow = EscrowAccount.get_main_account()
            
            # Create refund transaction
            EscrowTransaction.objects.create(
                order=self,
                transaction_type='refund',
                amount=self.total_amount,
                status='completed',
                notes=reason or f"Refund for cancelled order {self.order_id}",
                completed_at=timezone.now()
            )
            
            # Update escrow
            escrow.total_held -= self.total_amount
            escrow.total_balance -= self.total_amount
            escrow.save()
            
            # Remove from seller pending balance
            for item in self.items.all():
                try:
                    wallet = SellerWallet.objects.get(seller=item.product.seller)
                    wallet.pending_balance -= item.seller_payout
                    wallet.save()
                except SellerWallet.DoesNotExist:
                    pass
            
            # Update order
            self.escrow_status = 'refunded'
            Order.objects.filter(pk=self.pk).update(escrow_status='refunded')
            
            return True
        return False

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
        self.total_price = Decimal(str(self.quantity)) * Decimal(str(self.price_per_unit))
        rate = PlatformCommission.get_platform_commission()
        self.commission_rate = Decimal(str(rate))
        self.commission_amount = self.calculate_commission()
        self.seller_payout = self.total_price - self.commission_amount
        super().save(*args, **kwargs)

        if self.order:
            self.order.calculate_total()

    def calculate_commission(self):
        return (self.total_price * self.commission_rate / 100)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order {self.order.order_id}"



