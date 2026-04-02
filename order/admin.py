from django.contrib import admin
from .models import (
    Order, 
    OrderItem, 
    EscrowAccount, 
    EscrowTransaction, 
    SellerWallet
)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'commission_rate', 'commission_amount', 'seller_payout')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 
        'buyer', 
        'status', 
        'escrow_status',
        'total_amount', 
        'is_paid',
        'created_at'
    )
    list_filter = ('status', 'escrow_status', 'is_paid', 'created_at')
    search_fields = ('order_id', 'transaction_id', 'buyer__user__username', 'buyer__user__email')
    readonly_fields = (
        'order_id',
        'transaction_id',
        'subtotal',
        'total_amount',
        'platform_commission',
        'escrow_status',
        'escrow_held_at',
        'escrow_released_at',
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_id',
                'transaction_id',
                'buyer',
                'status',
                'note'
            )
        }),
        ('Customer Details', {
            'fields': (
                'address',
                'city'
            )
        }),
        ('Payment & Escrow', {
            'fields': (
                'is_paid',
                'escrow_status',
                'escrow_held_at',
                'escrow_released_at',
                'subtotal',
                'total_amount',
                'platform_commission'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'quantity',
        'price_per_unit',
        'total_price',
        'commission_amount',
        'seller_payout'
    )
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__order_id', 'product__name')
    readonly_fields = ('total_price', 'commission_rate', 'commission_amount', 'seller_payout')


@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = (
        'account_number', 
        'total_balance', 
        'total_held', 
        'total_released',
        'updated_at'
    )
    readonly_fields = (
        'account_number', 
        'total_balance', 
        'total_held', 
        'total_released',
        'created_at',
        'updated_at'
    )


@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 
        'transaction_type',
        'order',
        'amount', 
        'status',
        'created_at'
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = (
        'transaction_id', 
        'order__order_id',
        'gateway_transaction_id',
        'notes'
    )
    readonly_fields = (
        'transaction_id',
        'order',
        'transaction_type',
        'amount',
        'status',
        'gateway_transaction_id',
        'notes',
        'created_at',
        'completed_at'
    )
    date_hierarchy = 'created_at'


@admin.register(SellerWallet)
class SellerWalletAdmin(admin.ModelAdmin):
    list_display = (
        'seller',
        'available_balance',
        'pending_balance',
        'total_earned',
        'total_withdrawn',
        'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = (
        'seller__user__username',
        'seller__user__email',
        'seller__user__first_name',
        'seller__user__last_name'
    )
    readonly_fields = (
        'seller',
        'available_balance',
        'pending_balance',
        'total_earned',
        'total_withdrawn',
        'last_withdrawal_at',
        'created_at',
        'updated_at'
    )