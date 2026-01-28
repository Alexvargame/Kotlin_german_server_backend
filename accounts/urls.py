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
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('verification-success/', VerificationSuccessView.as_view(), name='verification_success'),
    path('sync-user/', SyncUserView.as_view()),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)