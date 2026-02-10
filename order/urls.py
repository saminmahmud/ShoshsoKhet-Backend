from django.urls import path
from .views import (
    OrderCreateView,
    BuyerOrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    OrderDeleteView,
    SellerOrderItemListView,
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
]


