from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer, OrderStatusSerializer, OrderStatusSerializer
from product.permissions import IsSellerOrAdmin, IsBuyerOrAdmin, IsAdmin, IsSeller, IsBuyer
from rest_framework import generics, viewsets, status
from django.core.exceptions import ValidationError


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBuyer]


class BuyerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBuyer]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user.buyer_profile).order_by('-created_at')
    

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBuyerOrAdmin]
    lookup_field = 'order_id'

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Order.objects.all()

        return Order.objects.filter(buyer=user.buyer_profile)
    
class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'order_id'

    def perform_update(self, serializer):
        order = serializer.instance
        new_status = self.request.data.get('status')

        if order.status == new_status:
            raise ValidationError("Order is already in this status")
        
        if order.status == 'delivered':
            raise ValidationError("Delivered order cannot be changed")
   
        serializer.save()


class OrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'order_id'


class SellerOrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get_queryset(self):
        return OrderItem.objects.filter(
            product__seller__user=self.request.user
        ).select_related(
            'product',
            'order'
        ).order_by('-order__created_at')
