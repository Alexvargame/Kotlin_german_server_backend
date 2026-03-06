from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    SupportMessageSendView,
    SupportMessageAdminAnswerSendView,
    CheckNewMessage,
    ReadedMessage,
    )

urlpatterns = [
    path('send_message/', SupportMessageSendView.as_view(), name='send_message'),
    path('answer_message/', SupportMessageAdminAnswerSendView.as_view(), name='answer_message'),
    path('check_new_message/', CheckNewMessage.as_view(), name='check_new_message'),
    path('readed_message/', ReadedMessage.as_view(), name='readed_message'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)