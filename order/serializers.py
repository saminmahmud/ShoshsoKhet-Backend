
from rest_framework import serializers
from .models import EscrowTransaction, Order, OrderItem, SellerWallet
from django.contrib.auth import get_user_model
from product.models import Product

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    seller_fullname = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all()) 
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'seller_fullname',
            'quantity',
            'price_per_unit',
            'total_price',
            'commission_rate',
            'commission_amount',
            'seller_payout'   
        ]
        read_only_fields = ['total_price', 'commission_rate', 'commission_amount', 'seller_payout']

    def get_seller_fullname(self, obj):
        return f"{obj.product.seller.user.first_name} {obj.product.seller.user.last_name}"
    


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    buyer_fullname = serializers.SerializerMethodField(read_only=True)
    escrow_status_display = serializers.CharField(source='get_escrow_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'transaction_id',
            'buyer_fullname',
            'address',
            'city',
            'status',
            'note',
            'escrow_status',
            'escrow_status_display',
            'escrow_held_at',
            'escrow_released_at',
            'subtotal',
            'total_amount',
            'platform_commission',
            'is_paid',
            'created_at',
            'updated_at',
            'items',
            'is_deleted'
        ]
        read_only_fields = ['order_id','subtotal', 'total_amount', 'platform_commission', 'created_at', 'updated_at', 'status', 'transaction_id', 'is_paid', 'escrow_status', 'escrow_held_at', 'escrow_released_at', 'is_deleted']


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        buyer = self.context['request'].user.buyer_profile

        order = Order.objects.create(buyer=buyer, **validated_data)

        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price_per_unit=item_data['price_per_unit']
            )

        order.calculate_total()
        return order
    
    def get_buyer_fullname(self, obj):
        return f"{obj.buyer.user.first_name} {obj.buyer.user.last_name}"
    

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class EscrowTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source='order.order_id', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EscrowTransaction
        fields = [
            'id',
            'transaction_id',
            'order',
            'order_id',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'status',
            'status_display',
            'gateway_transaction_id',
            'notes',
            'created_at',
            'completed_at'
        ]
        read_only_fields = ['transaction_id', 'created_at']


class SellerWalletSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.user.username', read_only=True)
    seller_fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SellerWallet
        fields = [
            'id',
            'seller',
            'seller_name',
            'seller_fullname',
            'available_balance',
            'pending_balance',
            'total_earned',
            'total_withdrawn',
            'last_withdrawal_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'available_balance',
            'pending_balance',
            'total_earned',
            'total_withdrawn',
            'last_withdrawal_at',
            'created_at',
            'updated_at'
        ]

    def get_seller_fullname(self, obj):
        return f"{obj.seller.user.first_name} {obj.seller.user.last_name}"
