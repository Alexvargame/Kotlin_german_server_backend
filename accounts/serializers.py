from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
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
        )

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
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
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