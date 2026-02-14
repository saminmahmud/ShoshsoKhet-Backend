from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlatformCommissionViewSet, PlatformRevenueViewSet

router = DefaultRouter()
router.register('commission', PlatformCommissionViewSet, basename='platform-commission')
router.register('revenue', PlatformRevenueViewSet, basename='platform-revenue')

urlpatterns = [
    path('', include(router.urls)),
]