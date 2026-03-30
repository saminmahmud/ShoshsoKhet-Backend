from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from accounts.views import (
    CustomTokenObtainPairView,
    UserDetailView,
    SellerProfileView,
    BuyerProfileView
)

router = DefaultRouter()
router.register('users', UserDetailView, basename='users')
router.register('seller-profiles', SellerProfileView, basename='seller-profiles')
router.register('buyer-profiles', BuyerProfileView, basename='buyer-profiles')


urlpatterns = [
    path('', include(router.urls)),
    
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('password-reset/', views.PasswordForgetOrChangeRequest.as_view(), name='password_reset'),
    path('password-reset-confirm/', views.SetPasswordView.as_view(), name='password_reset_confirm'),
]