from django.apps import AppConfig


class SupportChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'support_chat'

    def ready(self):
        import support_chat.signals
