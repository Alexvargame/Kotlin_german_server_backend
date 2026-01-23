from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    VerifyEmailView,
    ProfileView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('profile/', ProfileView.as_view()),
]
