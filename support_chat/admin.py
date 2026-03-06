from django.contrib import admin

from .models import Support_message

@admin.register(Support_message)
class Support_messageAdmin(admin.ModelAdmin):

    list_display = ('id', 'sender', 'receiver', 'text', 'reply_to', 'created_at', 'is_read')
