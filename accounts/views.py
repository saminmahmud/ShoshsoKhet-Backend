from concurrent.futures import thread
import threading
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import RegisterSerializer, ForgetOrChangePasswordSerializer, SetPasswordSerializer
from accounts.tasks import send_email
from accounts.utils import generate_email_token, verify_email_token, cleanup_expired_tokens
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenRefreshView


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




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"})
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)



@method_decorator(csrf_exempt, name='dispatch')
class PasswordForgetOrChangeRequest(APIView):
    permission_classes = []
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
        return super().post(request, *args, **kwargs)
