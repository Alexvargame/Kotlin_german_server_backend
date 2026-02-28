from django.contrib import admin
from .models import User, EmailVerification, PhoneVerification, UserGalleryAvatar

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'uid', 'username', 'score', 'streak_days', 'lifes',
                    'avatar_name', 'avatar_path', 'last_login_date',
                    'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'uid')
    list_filter = ('is_verified', 'is_active')

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_used', 'expires_at', 'created_at')
    search_fields = ('user__email', 'token')
    list_filter = ('is_used',)

@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_used', 'expires_at', 'created_at')
    search_fields = ('user__email', 'code')
    list_filter = ('is_used',)
@admin.register(UserGalleryAvatar)
class UserAvatarGallereyAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'is_active', 'created_at')
