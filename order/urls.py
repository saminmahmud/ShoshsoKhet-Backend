from django.urls import path
from .views import (
    OrderCreateView,
    BuyerOrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    OrderDeleteView,
    SellerOrderItemListView,
    Paymentview,
    Purchase,
    Cancle_or_Fail,
)

urlpatterns = [
    # Buyer
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('my-orders/', BuyerOrderListView.as_view(), name='buyer-order-list'),
    path('<uuid:order_id>/', OrderDetailView.as_view(), name='order-detail'),

    # Seller
    path('seller/order-items/', SellerOrderItemListView.as_view(), name='seller-order-items'),

    # Admin
    path('<uuid:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('<uuid:order_id>/delete/', OrderDeleteView.as_view(), name='order-delete'),

    # Payment callbacks
    path('payment/<uuid:order_id>/', Paymentview, name='payment-create'),
    path('payment/purchase/<uuid:order_id>/<tran_id>/', Purchase, name='purchase'),
    path('payment/cancle-or-fail/<uuid:order_id>/', Cancle_or_Fail, name='cancle-or-fail'),
]


