from rest_framework import serializers
from .models import Support_message
from django.utils import timezone


class SupportMessageSerializer(serializers.ModelSerializer):

    reply_to_text = serializers.SerializerMethodField()
    sender_UID = serializers.SerializerMethodField()
    receiver_UID = serializers.SerializerMethodField()

    class Meta:
        model = Support_message
        fields = (
            'sender',
            'sender_UID',
            'receiver',
            'receiver_UID',
            'text',
            'reply_to_text',
            'created_at',
            'is_read',
        )

    def get_reply_to_text(self, obj):
        if obj.reply_to:
            return obj.reply_to.text
        return None

    def get_receiver_UID(self, obj):
        if obj.receiver:
            return obj.receiver.uid
        return None

    def get_sender_UID(self, obj):
        if obj.sender:
            return obj.sender.uid
        return None