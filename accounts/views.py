import uuid

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone



from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, SyncProgressSerializer
from .models import User, EmailVerification

from accounts.utils import send_verification_email
#
# send_test_email('alex.direct.test@gmail.com')

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        print(email, username)
        user = User.objects.create_user(
            username=username,
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
        print(user.username, user, user.email, verification.token)

        send_verification_email(
            email=user.email,#'alex.direct.test@gmail.com', #user.email,
            token=verification.token
        )
        return Response({
            "uid": user.uid,
            "message": "Verification email sent",
            "email_token": str(verification.token),
            "username": user.username,
            "score": user.score,
            "streak_days": user.streak_days,
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

class SyncUserProgressiveView(APIView):
    permission_classes = []  # Не требует авторизации

    def post(self, request):

        uid = request.data.get('uid')
        if not uid:
            return Response({"error": "Uid is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        app_data = {
            "score": request.data.get('score'),
            "streak_days": request.data.get('shockmodLong'),
            "last_session_date": request.data.get('shockmodNow'),
        }
        if app_data["last_session_date"] is None:
            # Возвращаем данные сервера без обновления
            return Response({
                "success": True,
                "updated": False,
                "message": "No session date provided, using server data",
                "score": user.score,
                "streak_days": user.streak_days,
                "last_session_date": user.last_session_date if user.last_session_date else 0,
                "user": {
                    "uid": str(user.uid),
                    "email": user.email,
                    "username": user.username,
                    "is_verified": user.is_verified
                }
            })
        server_data = {
            'score': user.score,
            'streak_days': user.streak_days,
            'last_session_date': user.last_session_date if user.last_session_date else 0
        }
        app_date = app_data['last_session_date'] or 0
        server_date = server_data['last_session_date'] or 0
        if app_date > server_date:
            # Обновляем сервер данными из приложения
            user.score = app_data['score']
            user.streak_days = app_data['streak_days']
            user.last_session_date = app_data['last_session_date']
            user.save()
            updated = True
            returned_data = app_data
        else:
            # Используем данные сервера (они новее или равны)
            updated = False
            returned_data = server_data

        # Возвращаем все необходимые для синхронизации данные
        return Response({
            "success": True,
            "updated": updated,
            "message": "Server data updated" if updated else "Using server data",
            "score": returned_data['score'],
            "streak_days": returned_data['streak_days'],
            "last_session_date": returned_data['last_session_date'],
            "user": {
                "uid": str(user.uid),
                "email": user.email,
                "username": user.username,
                "is_verified": user.is_verified
            }
        }, status=status.HTTP_200_OK)

class ResendVerificationView(APIView):
    permission_classes = []  # Не требует авторизации

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Находим пользователя
            user = User.objects.get(email=email)

            # 2. Если уже верифицирован — ничего не делаем
            if user.is_verified:
                return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)

            # 3. Пытаемся найти существующий НЕиспользованный токен
            try:
                verification = EmailVerification.objects.get(user=user, is_used=False)

                # Проверяем, не истёк ли токен
                if verification.expires_at < timezone.now():
                    # Если истёк — помечаем как использованный и создаём новый
                    verification.is_used = True
                    verification.save()
                    raise EmailVerification.DoesNotExist  # Перейдём к созданию нового

            except EmailVerification.DoesNotExist:
                # Если нет активного токена — создаём новый (как при регистрации)
                email_token = uuid.uuid4()
                verification = EmailVerification.objects.create(
                    user=user,
                    token=email_token,
                    expires_at=timezone.now() + timezone.timedelta(hours=24),
                    is_used=False
                )

            # 4. Отправляем письмо с ЭТИМ токеном (старым или новым)
            send_verification_email(email=user.email, token=verification.token)

            return Response({
                "message": "Verification email sent",
                "email": user.email,
                "token": str(verification.token)
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteUserView(APIView):
    permission_classes = []  # Не требует авторизации

    def delete(self, request, uid):  # Принимаем uid из URL
        try:
            user = User.objects.get(uid=uid)  # Ищем по полю uid
            print(user, user.uid)
            user.delete()
            return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)