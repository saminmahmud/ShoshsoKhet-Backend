from rest_framework import serializers
from .models import PlatformCommission, PlatformRevenue


class PlatformCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformCommission
        fields = ['id', 'commission_rate', 'updated_at']
        read_only_fields = ['id', 'updated_at']


# class PlatformRevenueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PlatformRevenue
#         fields = ['id', 'revenue_type', 'order', 'seller', 'buyer', 'amount', 'description', 'transaction_id', 'created_at']
#         read_only_fields = ['id', 'created_at']

class PlatformRevenueSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source='order.order_id', read_only=True)
    seller_name = serializers.CharField(source='seller.user.username', read_only=True)
    buyer_name = serializers.CharField(source='buyer.user.username', read_only=True)

    class Meta:
        model = PlatformRevenue
        fields = [
            'id',
            'revenue_type',
            'order',
            'order_id',
            'seller',
            'seller_name',
            'buyer',
            'buyer_name',
            'amount',
            'description',
            'transaction_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'order_id', 'seller_name', 'buyer_name']