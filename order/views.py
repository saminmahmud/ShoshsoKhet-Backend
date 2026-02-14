from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated
from sslcommerz_lib import SSLCOMMERZ
from order.utils import generate_transaction_id
from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer, OrderStatusSerializer, OrderStatusSerializer
from product.permissions import IsSellerOrAdmin, IsBuyerOrAdmin, IsAdmin, IsSeller, IsBuyer
from rest_framework import generics, viewsets, status
from django.core.exceptions import ValidationError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import json



STORE_ID = settings.STORE_ID
STORE_PASSWORD = settings.STORE_PASSWORD
BACKEND_URL = settings.BACKEND_URL
FRONTEND_URL = settings.FRONTEND_URL

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


# Payment Gateway Integration


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def Paymentview(request, order_id):
    if request.method == 'POST':
        try:
            order_qs = Order.objects.get(id=order_id, is_paid=False)
            order_total = order_qs.total_price
            
            tran_id = generate_transaction_id()

            store_settings = {
                'store_id': STORE_ID,  
                'store_pass': STORE_PASSWORD,
                'issandbox': True 
            }
            sslcz = SSLCOMMERZ(store_settings)
            
            post_body = {
                'total_amount': order_total,
                'currency': "BDT",
                'tran_id': tran_id,
                'success_url': f"{BACKEND_URL}/order/payment/purchase/{order_id}/{tran_id}/",
                'fail_url': f"{BACKEND_URL}/order/payment/cancle-or-fail/{order_id}/",
                'cancel_url': f"{BACKEND_URL}/order/payment/cancle-or-fail/{order_id}/",
                'emi_option': 0,
                'cus_name': f'{order_qs.first_name} {order_qs.last_name}',
                'cus_email': order_qs.email,
                'cus_phone': order_qs.phone,
                'cus_add1': order_qs.address,
                'cus_city': order_qs.city,
                'cus_country': "Bangladesh",
                'shipping_method': "NO",
                'num_of_item': order_qs.items.count(),
                'product_name': "Test",
                'product_category': "Test Category",
                'product_profile': "general"
            }

            # Call SSLCommerz to create a session
            response = sslcz.createSession(post_body)

            # Check if the response contains the required data
            if 'GatewayPageURL' not in response:
                return JsonResponse({'error': 'Failed to create SSLCommerz session'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return JsonResponse({'redirect_url': response['GatewayPageURL']}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# View to handle the success response from the payment gateway
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def Purchase(request, order_id, tran_id):
    order_qs = Order.objects.get(id=order_id, is_paid=False)
    
    if order_qs:
        order_qs.is_paid = True
        order_qs.tran_id = tran_id
        order_qs.save()
        return HttpResponseRedirect(f'{FRONTEND_URL}/my-orders?payment_status=success')

    return HttpResponseRedirect(f'{FRONTEND_URL}/cart?payment_status=failed')


# View to handle the failure or cancellation of the payment
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def Cancle_or_Fail(request, order_id):
    order_qs = Order.objects.get(id=order_id, is_paid=False)
    
    if order_qs:
        order_qs.delete()
        return HttpResponseRedirect(f'{FRONTEND_URL}/cart?payment_status=failed')

    return HttpResponseRedirect(f'{FRONTEND_URL}/cart?payment_status=failed')