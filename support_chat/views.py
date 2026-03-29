from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import datetime

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .models import Support_message
from .serializers import SupportMessageSerializer
from .utils import send_push
from accounts.models import User, Device


class SupportMessageSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        print('REQUETE', request.data)

        receiver = User.objects.get(uid=request.data.get('receiver_uid'))
        text = request.data.get('text')
        print(receiver, text)
        message = Support_message.objects.create(
            sender=user,
            receiver=receiver,
            text=text
        )
        print(message)
        # devices = user.devices.all()
        # print('DEV', devices)
        # title = "Внимание"
        # body = "У вас новое сообщение"
        #
        # data_fcm = {'user_uid': str(user.uid), 'email': user.email}
        # for device in devices:
        #     send_push(device.fcm_token, title, body, data_fcm)

        return Response(
            {
            "id": message.id,
            "sender": {
                "id": message.sender.id,
                "uid": message.sender.uid,
                "username": message.sender.username
            },
            "receiver": {
                "id": message.receiver.id,
                "uid": message.receiver.uid,
                "username": message.receiver.username
            },
            "text": message.text,
            "created_at": message.created_at,
            "is_read": message.is_read,
        })

class SupportMessageAdminAnswerSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print('REQUETE', request.data)

        sender = User.objects.filter(is_staff=True).first()
        try:
            alt_message = Support_message.objects.get(id=request.data.get("alt_message"))
        except:
            return Response(f"Это сообщение удалено")

        receiver = alt_message.sender
        answer = request.data.get('answer')
        text = alt_message.text
        print(receiver, text, answer)
        message = Support_message.objects.create(
            sender=sender,
            receiver=receiver,
            text=answer,
            reply_to=alt_message,
        )
        if not receiver.is_staff:
            alt_message.is_read = True
            alt_message.save()
        print(message)
        devices = receiver.devices.all()
        print('DEV', devices)
        title = "Внимание"
        body = "У вас новое сообщение"

        data_fcm = {'user_uid': str(receiver.uid), 'email': receiver.email}
        for device in devices:
            send_push(device.fcm_token, title, body, data_fcm)

        return Response({
            "id": message.id,
            "atl_message_id": alt_message.id,
            "sender": {
                "id": message.sender.id,
                "uid": message.sender.uid,
                "username": message.sender.username
            },
            "receiver": {
                "id": message.receiver.id,
                "uid": message.receiver.uid,
                "username": message.receiver.username
            },
            "text": message.text,
            "reply_to": alt_message.text,
            "created_at": message.created_at,
            "is_read": message.is_read
        })


class CheckNewMessage(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):

        print('REQUEST_DATA2', request.query_params)

        last_message_id = request.query_params.get("last_message_id")
        messages = Support_message.objects.filter(
            receiver=request.user, id__gt=last_message_id)
        print('MESS', messages)
        for m in messages:
            print('M_DICT', m.__dict__)
        serializer = SupportMessageSerializer(messages, many=True)
        return Response(serializer.data)


class ReadedMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('REQUETE', request.data)
        ids = request.data.get("message_ids")
        print('Res/last',  ids)
        messages = Support_message.objects.filter(
            receiver=request.user, id__in=ids).update(is_read=True)
        if not messages:
            return Response(f"Новых прочитанных сообщений у пользователя нет")
        return Response({"status": 'Ok'})


class SupportMessageDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        server_id = request.data.get("server_id")
        print('SErver_id', server_id)
        if not server_id:
            return Response(
                {"detail": "server_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            message = Support_message.objects.get(id=server_id)
            print('Mess', message)
        except Support_message.DoesNotExist:
            return Response(
                {"detail": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # проверяем, что пользователь может удалить только свои сообщения
        print('senndUid', message.sender.uid, 'req_user', request.user.uid)
        if message.sender.uid != request.user.uid:
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN
            )

        message.delete()
        return Response({"status": "deleted"}, status=status.HTTP_200_OK)