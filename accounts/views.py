from concurrent.futures import thread
import threading
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.models import BuyerProfile, SellerProfile
from accounts.serializers import BuyerDashboardSerializer, RegisterSerializer, ForgetOrChangePasswordSerializer, SellerDashboardSerializer, SetPasswordSerializer, UserSerializer, SellerProfileSerializer, BuyerProfileSerializer, CustomTokenObtainPairSerializer
from accounts.tasks import send_email
from accounts.utils import generate_email_token, verify_email_token, cleanup_expired_tokens
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = generate_email_token(user)
        confirmation_link = f"{settings.BACKEND_URL}/accounts/verify-email/?token={token}"

        # send email by html file 
        subject = "Verify Your Email"
        body = render_to_string("activation_email.html", {
            "user": user,
            "confirmation_link": confirmation_link,
        })

        email_thread = threading.Thread(target=send_email, args=(subject, body, user.email))
        email_thread.start()

        return Response({"message": "Registration successful. Please check your email to verify your account."}, status=201)


class VerifyEmailView(APIView):
    serializer_class = None
    
    def get(self, request):
        token = request.GET.get('token')
        email = verify_email_token(token)

        if email:
            try:
                user = User.objects.get(email=email)
                user.is_verified = True
                user.save()
                return HttpResponseRedirect(settings.FRONTEND_URL + "/login?status=success")
            except User.DoesNotExist:
                return HttpResponseRedirect(settings.FRONTEND_URL + "/login?status=failed")
        else:
            return HttpResponseRedirect(settings.FRONTEND_URL + "/login?status=failed")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access  = str(serializer.validated_data['access'])
        refresh = str(serializer.validated_data['refresh'])

        response = Response({'access': access}, status=200)

        response.set_cookie(
            key='refresh',
            value=refresh,
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', True),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'None'),
            max_age=60 * 60 * 24 * 30, 
        )
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

        response = Response({"message": "Logout successful"})
        response.delete_cookie('refresh', samesite='None')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class PasswordForgetOrChangeRequest(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = ForgetOrChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if not email:
            return Response({"error": "Email required"}, status=400)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "If the email exists, a reset link has been sent."},
                status=200
            )

        token = generate_email_token(user)
        reset_link = f"{settings.BACKEND_URL}/accounts/set-password/?token={token}"

        subject = "Set Your Password"
        body = render_to_string("password_reset_email.html", {
            "user": user,
            "reset_link": reset_link,
        })

        email_thread = threading.Thread(target=send_email, args=(subject, body, user.email))
        email_thread.start()

        return Response({"message": "Password reset link sent to your email."}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SetPasswordView(APIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = SetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        email = verify_email_token(token)

        if not email:
            return Response(
                {"error": "Invalid or expired token."},
                status=400
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=404
            )
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful."}, status=200)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        cleanup_expired_tokens()

        refresh_token = request.COOKIES.get('refresh')
        if refresh_token:
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data['refresh'] = refresh_token
            request._full_data = data

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and 'refresh' in response.data:
            new_refresh = response.data.pop('refresh')
            response.set_cookie(
                key='refresh',
                value=new_refresh,
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', True),
                samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'None'),
                max_age=60 * 60 * 24 * 30,
            )
        return response


class UserDetailView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

class SellerProfileView(ModelViewSet):
    serializer_class = SellerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == 'admin':
            return SellerProfile.objects.select_related('user').all()

        if user.user_type == 'seller':
            return SellerProfile.objects.filter(user=user)
        return SellerProfile.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type != 'seller':
            raise PermissionDenied("Only sellers can create profile.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    

class BuyerProfileView(ModelViewSet):
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == 'admin':
            return BuyerProfile.objects.select_related('user').all()

        if user.user_type == 'buyer':
            return BuyerProfile.objects.filter(user=user)

        return BuyerProfile.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type != 'buyer':
            raise PermissionDenied("Only buyers can create profile.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)



class SellerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, seller_id):
        seller = get_object_or_404(SellerProfile, id=seller_id)
        serializer = SellerDashboardSerializer(seller)
        return Response(serializer.data)


class BuyerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, buyer_id):
        buyer = get_object_or_404(BuyerProfile, id=buyer_id)
        serializer = BuyerDashboardSerializer(buyer)
        return Response(serializer.data)