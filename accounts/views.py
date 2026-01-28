import uuid

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User, EmailVerification

from accounts.utils import send_verification_email
#
# send_test_email('alex.direct.test@gmail.com')

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        print(email)
        user = User.objects.create_user(
            email=email,
            password=password
        )
        email_token = uuid.uuid4()
        verification = EmailVerification.objects.create(
            user=user,
            token=email_token,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
            is_used=False
        )
        print(user, user.email, verification.token)

        send_verification_email(
            email=user.email,#'alex.direct.test@gmail.com', #user.email,
            token=verification.token
        )
        return Response({
            "uid": user.uid,
            "message": "Verification email sent",
            "email_token": str(verification.token),
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request):
        email_token = request.query_params.get('token')
        if not email_token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            verification = EmailVerification.objects.get(token=email_token, is_used=False)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)

        if verification.expires_at < timezone.now():
            return Response({"error": "Token expired"}, status=400)
        verification.user.is_verified = True
        verification.user.save()

        verification.is_used = True
        verification.save()

        return redirect(reverse('verification_success'))
        #return Response({"status": "verified"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        print('USER', user)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)
        if not user.is_verified:
            return Response({"error": "Email not verified"}, status=403)
        login_token, _ = Token.objects.get_or_create(user=user)
        print('LOGIN_TOKEN', login_token)

        return Response({
            "login_token": login_token.key,
            "uid": user.uid
        })



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print('PROFILE')
        serializer = UserSerializer(request.user)
        print(serializer.data)
        return Response(serializer.data)



class VerificationSuccessView(TemplateView):
    template_name = 'verification_success.html'


class SyncUserView(APIView):
    permission_classes = []  # Не требует авторизации

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем токен пользователя
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)

        # Возвращаем все необходимые для синхронизации данные
        return Response({
            "uid": str(user.uid),
            "email": user.email,
            "is_verified": user.is_verified,
            "login_token": token.key
        }, status=status.HTTP_200_OK)


