from rest_framework import serializers
from .models import Support_message
from django.utils import timezone


class SupportMessageSerializer(serializers.ModelSerializer):

    reply_to_text = serializers.SerializerMethodField()

    class Meta:
        model = Support_message
        fields = (
            'sender',
            'receiver',
            'text',
            'reply_to_text',
            'created_at',
            'is_read',
        )

    def get_reply_to_text(self, obj):
        if obj.reply_to:
            return obj.reply_to.text
        return None