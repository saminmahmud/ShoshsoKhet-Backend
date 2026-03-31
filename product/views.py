from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from product.filters import ProductFilter

from product.filters import ProductFilter
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductSerializer,
)
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsBuyerOrAdmin, IsSeller, IsBuyer, IsAdmin, IsSellerOrAdmin, IsSellerOwner


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        # Anyone logged in can READ
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        # Only admin can CREATE / UPDATE / DELETE
        return [permissions.IsAuthenticated(), IsAdmin()]
    

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'category__name']
    ordering_fields = ['price_per_unit', 'created_at']

    def get_queryset(self):
        user = self.request.user

        # Admin sees all
        if user.user_type == 'admin':
            return Product.objects.all()

        # Seller sees own products
        if user.user_type == 'seller':
            return Product.objects.filter(seller=user.seller_profile)

        # Buyer sees active products only
        return Product.objects.filter(is_active=True)

    def get_permissions(self):
        # Read-only for buyers
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]

        # Create / Update / Delete → Seller or Admin
        return [permissions.IsAuthenticated(), IsSellerOrAdmin()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.user_type == 'seller':
            serializer.save(seller=user.seller_profile)
        else:
            serializer.save()  # admin case

    def perform_update(self, serializer):
        user = self.request.user

        if user.user_type == 'seller':
            serializer.save(seller=user.seller_profile)
        else:
            serializer.save()

    def get_object(self):
        obj = super().get_object()

        # Seller cannot access others product
        if self.request.user.user_type == 'seller':
            if obj.seller.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Not your product.")

        return obj
