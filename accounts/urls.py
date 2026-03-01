from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    RegisterView,
    LoginView,
    VerifyEmailView,
    ProfileView,
    VerificationSuccessView,
    SyncUserView,
    ResendVerificationView,
    DeleteUserView,
    SyncUserProgressiveView,
    RatingView,
    UploadGalleryAvatarView,
    SelectActiveGalleryAvatarView,
    DeleteGalleryAvatarView,
    SyncUserAvatarView,
    SyncUserGalleryAvatarView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('verification-success/', VerificationSuccessView.as_view(), name='verification_success'),
    path('sync-user/', SyncUserView.as_view()),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    path('delete/<str:uid>/', DeleteUserView.as_view(), name='delete_user'),
    path('sync-progress/', SyncUserProgressiveView.as_view(), name='sync_progress'),
    path('rating/', RatingView.as_view(), name='rating'),
   # path("upload-gallery-avatar/", UploadGalleryAvatarView.as_view()),
    path("select-active-avatar/", SelectActiveGalleryAvatarView.as_view()),
    path("delete-avatar/", DeleteGalleryAvatarView.as_view()),
    path("upload-avatar/", SyncUserAvatarView.as_view()),
    path("upload-gallery-avatar/", SyncUserGalleryAvatarView.as_view()),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)