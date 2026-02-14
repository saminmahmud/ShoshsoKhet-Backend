from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'commission_rate', 'commission_amount', 'seller_payout')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'transaction_id', 'buyer', 'status',  'subtotal', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'buyer__user__username', 'buyer__user__email')
    readonly_fields = (
        'order_id',
        'transaction_id',
        'subtotal',
        'total_amount',
        'created_at',
        'updated_at',
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'quantity',
        'price_per_unit',
        'total_price',
        'commission_rate',
        'commission_amount',
        'seller_payout'
    )

    search_fields = ('order__order_id', 'product__name')
    readonly_fields = ('total_price', 'commission_rate', 'commission_amount', 'seller_payout')
