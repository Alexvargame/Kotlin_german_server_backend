import uuid

from rest_framework.permissions import AllowAny
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import datetime



from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, SyncProgressSerializer
from .models import User, EmailVerification, UserGalleryAvatar

from accounts.utils import send_verification_email, get_max_gallery_avatars
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
        print('rewuest', request.data)
        uid = request.data.get('uid')
        if not uid:
            return Response({"error": "Uid is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        app_data = {
            "score": request.data.get('score'),
            "streak_days": request.data.get('streak_days'),
            "lifes": request.data.get('lifes'),
            "last_session_date": request.data.get('last_session_date'),
        }
        print('APP_DATA', app_data)
        if app_data["last_session_date"] is None:
            # Возвращаем данные сервера без обновления
            return Response({
                "success": True,
                "updated": False,
                "message": "No session date provided, using server data",
                "score": user.score,
                "streak_days": user.streak_days,
                "lifes": user.lifes,
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
            'lifes': user.lifes,
            'last_session_date': user.last_session_date if user.last_session_date else 0
        }
        print("SERVER DATA", server_data)
        app_date = app_data['last_session_date'] or 0
        server_date = server_data['last_session_date'] or 0
        print(app_data['last_session_date'], server_data['last_session_date'])
        if app_date >= server_date:
            # Обновляем сервер данными из приложения
            user.score = app_data['score']
            user.streak_days = app_data['streak_days']
            user.lifes = app_data['lifes']
            user.last_session_date = app_data['last_session_date']
            user.save()
            updated = True
            returned_data = app_data
            print('USER', user)

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
            "lifes": returned_data['lifes'],
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
        
class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print('RATING', request.user)
        score_users = User.objects.all().order_by('-score')
        score_users_list = list(score_users.values_list('id', flat=True))
        try:
            current_user_score_rank = score_users_list.index(request.user.id) + 1
        except ValueError:
            current_user_score_rank = None
        score_users = score_users[:10]

        shockmod_users = User.objects.all().order_by('-streak_days')[:10]
        score_shockmod_list = list(shockmod_users.values_list('id', flat=True))
        try:
            current_user_shockmod_rank = score_shockmod_list.index(request.user.id) + 1
        except ValueError:
            current_user_shockmod_rank = None
        shockmod_users = shockmod_users[:10]
        serializer_score = UserSerializer(score_users, many=True)
        serializer_shockmod = UserSerializer(shockmod_users, many=True)
        print("SCORE",serializer_score.data)
        print("SHOCK", serializer_shockmod.data)
        return Response(
            {
                'score_rating':
                    {
                        'type': 'score',
                        'top': serializer_score.data,
                        'current_user_rank': current_user_score_rank,
                    },
                'shockmod_rating':
                    {
                        'type': 'shockmod',
                        'top': serializer_shockmod.data,
                        'current_user_rank': current_user_shockmod_rank,
                    },
                }
        )
class UploadGalleryAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        max_allowed = get_max_gallery_avatars(user.score)
        current_count = user.gallery_avatars.count()

        if current_count >= max_allowed:
            return Response(
                {"error": "Avatar limit reached"},
                status=status.HTTP_400_BAD_REQUEST
            )
        image =request.FILES.get('image')
        if not image:
            return Response(
                {"error": "NO IMAGE PROVIDED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        avatar = UserGalleryAvatar.objects.create(
            user=user,
            image=image,
            is_active=False
        )
        user.avatar_last_changed = timezone.now()
        user.save()

        return Response(
            {
                "id": avatar.id,
                "image_url": avatar.image.url
            },
            status=status.HTTP_201_CREATED
        )


class SelectActiveGalleryAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        image_file = request.FILES.get('image')
        print(request.data)
        if not image_file:
            return Response({"error": "No image provided"}, status=400)
        filename = image_file.name

        try:
            # Ищем аватар пользователя по имени файла
            avatar = user.gallery_avatars.get(image__icontains=filename)
        except UserGalleryAvatar.DoesNotExist:
            return Response({"error": "Avatar not found"}, status=404)

        # Сбрасываем все остальные аватары
        user.gallery_avatars.update(is_active=False)

        # Делаем выбранный аватар активным
        avatar.is_active = True
        avatar.save()

        # Обновляем у пользователя
        user.active_gallery_avatar = avatar
        user.avatar_last_changed = timezone.now()
        user.save()

        return Response({
            "id": avatar.id,
            "image_url": avatar.image.url,
            "avatar_last_changed": user.avatar_last_changed
        }, status=200)

class DeleteGalleryAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        image_file = request.FILES.get('image')
        print(request.data)
        print(request.FILES)

        if not image_file:
            return Response({"error": "No image provided"}, status=400)

        filename = image_file.name

        try:
            avatar = user.gallery_avatars.get(image__icontains=filename)
        except UserGalleryAvatar.DoesNotExist:
            return Response({"error": "Avatar not found"}, status=404)
        # Если удаляем активный аватар, сбрасываем активный
        if avatar.is_active:
            user.gallery_avatars.update(is_active=False)

        avatar.delete()
        user.avatar_last_changed = timezone.now()
        user.save()

        return Response({"status": "deleted", "avatar_last_changed": user.avatar_last_changed})

class SyncUserAvatarView(APIView):
    permission_classes = []  # Не требует авторизации

    def post(self, request):
        print('AVA_rewuest', request.data)
        uid = request.data.get('uid')
        if not uid:
            return Response({"error": "Uid is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        app_data = {
            "avatar_name": request.data.get('avatar_name'),
            "avatar_last_changed": request.data.get('avatar_last_changed'),
        }
        print('AVA_APP_DATA', app_data)
        if app_data["avatar_last_changed"] is None:
            # Возвращаем данные сервера без обновления
            return Response({
                "success": True,
                "updated": False,
                "message": "No session date provided, using server data",
                "score": user.score,
                "avatar_name": user.avatar_name,
                "avatar_last_changed": user.avatar_last_changed if user.avatar_last_changed else 0,
                "user": {
                    "uid": str(user.uid),
                    "email": user.email,
                    "username": user.username,
                    "is_verified": user.is_verified
                }
            })
        server_data = {
            'score': user.score,
            'avatar_name': user.avatar_name,
            'avatar_last_changed': user.avatar_last_changed if user.avatar_last_changed else 0
        }
        print("AVA_SERVER DATA", server_data)
        app_avatar_date = app_data['avatar_last_changed'] or 0
        server_avatar_date = server_data['avatar_last_changed'] or 0
        server_avatar_date = int(server_avatar_date.timestamp() * 1000)
        print("AVA_",app_avatar_date, server_avatar_date)
        if app_avatar_date > server_avatar_date:
            # Обновляем сервер данными из приложения
            user.avatar_last_changed = datetime.datetime.utcfromtimestamp(app_avatar_date / 1000).replace(tzinfo=datetime.timezone.utc)
            user.avatar_name = app_data['avatar_name']
            user.save()
            updated = True
            returned_data = app_data
            print('USER', user)

        else:
            # Используем данные сервера (они новее или равны)
            updated = False
            returned_data = server_data

        # Возвращаем все необходимые для синхронизации данные
        return Response({
            "success": True,
            "updated": updated,
            "message": "Server data updated" if updated else "Using server data",
            "avatar_name": returned_data['avatar_name'],
            "avatar_last_changed": returned_data['avatar_last_changed'],
            "user": {
                "uid": str(user.uid),
                "email": user.email,
                "username": user.username,
                "is_verified": user.is_verified
            }
        }, status=status.HTTP_200_OK)


class SyncUserGalleryAvatarView(APIView):
    # permission_classes = [IsAuthenticated]  # Не требует авторизации
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        print('AVA_GAL_rewuest', request.data)
        uid = request.data.get('uid')
        timestamp = request.data.get('avatar_last_changed')
        image_file = request.FILES.get('file')
        print(uid, timestamp, image_file)
        if not uid:
            return Response({"error": "Uid is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        avatar = UserGalleryAvatar.objects.create(
            user=user,
            image=image_file,
            is_active=True
        )
        UserGalleryAvatar.objects.filter(user=user, is_active=True).exclude(id=avatar.id).update(is_active=False)

        user.avatar_name = avatar.image.name
        user.avatar_last_changed = timezone.now()
        user.save()
        return Response({
            "success": True,
            "updated": False,
            "message": "No session date provided, using server data",
            "score": user.score,
            "avatar_name": user.avatar_name,
            "avatar_last_changed": user.avatar_last_changed if user.avatar_last_changed else 0,
            "user": {
                "uid": str(user.uid),
                "email": user.email,
                "username": user.username,
                "is_verified": user.is_verified
            }
        }, status=status.HTTP_200_OK)
