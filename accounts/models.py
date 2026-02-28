import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

import datetime


def default_email_expiry():
    return timezone.now() + datetime.timedelta(hours=24)


def default_phone_expiry():
    return timezone.now() + datetime.timedelta(minutes=10)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username,  email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        if not username:
            raise ValueError('Username must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('score', 0)
        extra_fields.setdefault('streak_days', 0)
        extra_fields.setdefault('last_login_date', None)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        username = extra_fields.pop('username', None)
        if not username:
            # Генерируем username из email, если не передан
            username = email.split('@')[0]

        return self.create_user(username,email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    score = models.IntegerField(default=0)  # Баллы
    lives = models.IntegerField(default=5)
    streak_days = models.IntegerField(default=0)  # Текущая серия (shockmodLong)
    username = models.CharField(max_length=100, null=True, blank=True, default='')  # Никнейм
    last_login_date = models.DateTimeField(null=True, blank=True)  # Дата последнего входа
    last_session_date = models.BigIntegerField(null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_name = models.CharField(max_length=100, null=True, blank=True)
    avatar_path = models.CharField(max_length=100, null=True, blank=True)


    avatar_last_changed = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email




class EmailVerification(models.Model):

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='email_verifications')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField(default=default_email_expiry())
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"


class PhoneVerification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='phone_verifications')
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField(default=default_phone_expiry())
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone} - {self.code}"


def user_avatar_path(instance, filename):
    return f"uploads/gallery_avatars/user_{instance.user.id}/{filename}"


class UserGalleryAvatar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_avatars')
    image = models.ImageField(upload_to=user_avatar_path)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.image}"