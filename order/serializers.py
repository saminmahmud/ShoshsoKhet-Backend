
from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    seller_fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'seller_fullname',
            'quantity',
            'price_per_unit',
            'total_price'
        ]
        read_only_fields = ['total_price']

    def get_seller_fullname(self, obj):
        return f"{obj.product.seller.user.first_name} {obj.product.seller.user.last_name}"
    


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    buyer_fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'buyer',
            'buyer_fullname',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'status',
            'note',
            'total_amount',
            'platform_commission',
            'delivery_fee',
            'created_at',
            'updated_at',
            'items'
        ]
        read_only_fields = ['order_id', 'total_amount', 'platform_commission', 'created_at', 'updated_at', 'status']


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
                price_per_unit=product.price
            )

        order.calculate_total()
        return order
    
    def get_buyer_fullname(self, obj):
        return f"{obj.buyer.user.first_name} {obj.buyer.user.last_name}"
    

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
