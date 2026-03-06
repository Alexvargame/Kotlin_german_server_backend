from django.db import models

from accounts.models import User

class Support_message(models.Model):

    sender = models.ForeignKey(User, related_name='message_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='message_receiver', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Саппорт_сообщение"
        verbose_name_plural = "Саппорт_сообщения"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.id} to {self.receiver.id} text {self.text}"
