# support_chat/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Support_message
from .utils import send_push


@receiver(post_save, sender=Support_message)
def send_notification_on_message(sender, instance, created, **kwargs):
    """
    Автоматически отправляет push-уведомление при создании нового сообщения
    """
    if created:
        # срабатывает только при создании, не при обновлении
        # Получаем токен устройства получателя
        # Здесь логика: у instance есть связь с пользователем-получателем
        # и у пользователя есть fcm_token

        recipient = instance.receiver  # пример, подставь своё поле
        fcm_token = recipient.fcm_token  # пример, подставь своё поле

        if fcm_token:
            send_push(
                token=fcm_token,
                title="Новое сообщение",
                body=instance.text[:100],  # первые 100 символов
                data={"message_id": str(instance.id)}
            )