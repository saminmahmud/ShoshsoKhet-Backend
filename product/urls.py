from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GetSellerProductsViewSet, ProductViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('seller-products/', GetSellerProductsViewSet.as_view({'get': 'list'}), name='seller-products'),
]
