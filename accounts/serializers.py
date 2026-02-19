from rest_framework import serializers
from .models import User, UserGalleryAvatar
from django.utils import timezone
class UserSerializer(serializers.ModelSerializer):
    avatar_name = serializers.CharField(read_only=True)
    active_gallery_avatar_url = serializers.SerializerMethodField()
    avatar_last_changed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'uid',
            'email',
            'username',
            'score',
            'streak_days',
            'phone',
            'is_verified',
            'created_at',
            'last_session_date',
            'avatar_name',
            'active_gallery_avatar_url',
            'avatar_last_changed',
        )

    def get_active_gallery_avatar_url(self, obj):
        active_avatar = obj.gallery_avatars.filter(is_active=True).first()
        if active_avatar:
            return active_avatar.image.url
        return None

    def get_avatar_last_changed(self, obj):
        if obj.avatar_last_changed:
            return int(obj.avatar_last_changed.timestamp() * 1000)  # миллисекунды
        return 0

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(
        max_length=100,
        required=True
    )
    def validate_username(self, value):
        """Валидация username"""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        # if len(value) < 3:
        #     raise serializers.ValidationError("Username must be at least 3 characters")
        if len(value) > 100:
            raise serializers.ValidationError("Username is too long")
        return value.strip()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SyncProgressSerializer(serializers.Serializer):
    uid = serializers.UUIDField()
    score = serializers.IntegerField(min_value=0)
    streak_days = serializers.IntegerField(min_value=0)
    last_session_date = serializers.IntegerField(min_value=0, allow_null=True)


class GalleryAvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGalleryAvatar
        fields = ['id', 'image', 'is_active', 'created_at']

# class SelectActiveAvatarSerializator(serializers.Serializer):
#     avatar_id = serializers.IntegerField()
#
#     def validate_avatar_id(self, value):
#         user =self.context['request'].user
#         if not user.gallery_avatars.filter(id=value).exists():
#             raise serializers.ValidationError("Аватар не найден или не принадлежит пользователю")
#         return value
#
#     def set_active_avatar(user, avatar_id):
#         # Деактивируем все аватары пользователя
#         user.gallery_avatars.update(is_active=False)
#         # Активируем выбранный
#         avatar = user.gallery_avatars.get(id=avatar_id)
#         avatar.is_active = True
#         avatar.save()
#         # Обновляем время последнего изменения
#         user.avatar_last_changed = timezone.now()
#         user.save()
