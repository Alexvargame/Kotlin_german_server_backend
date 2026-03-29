# support_chat/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Support_message
from accounts.models import Device
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

        devices = Device.objects.filter(user=instance.receiver)

        for device in devices:
            send_push(
                fcm_token=device.fcm_token,
                title="Внимание",
                body="У вас новое сообщение",
                data=
                    {
                        'user_uid': str(instance.sender.uid),
                     'email': instance.sender.email
                     }
            )