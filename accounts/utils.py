# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings
import os
from .sendgrid_helper import send_email_via_sendgrid_api
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
def send_test_email(to_email):
    send_mail(
        subject='Test Email',
        message='Hello! This is a test from Django + SendGrid',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )

# def send_verification_email(email, token):
#     verify_url = f'http://127.0.0.1:8000/api/verify-email/?token={token}'
#     send_mail(
#         subject='Test Email',
#         message=(
#             'Please verify your email by clicking the link:\n\n'
#             f'{verify_url}'
#         ),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[email],
#         fail_silently=False,
#     )
#
# def send_verification_email(email, token):
#     verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'
#     try:
#         send_mail(
#             subject='Verify your email',
#             message=f'Click to verify: {verify_url}',
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[email],
#             fail_silently=False,
#         )
#         print(f"✅ Email sent to {email}")
#     except Exception as e:
#         print(f"❌ Email send failed: {e}")
#         # Не поднимай исключение, чтобы не ломать регистрацию


def send_verification_email(email, token):
    verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'

    # Проверяем, находимся ли на PythonAnywhere
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:  # Более надёжный способ
        try:
            return send_email_via_sendgrid_api(email, token)
        except ImportError as e:
            print(f"⚠️ Cannot import SendGrid helper: {e}")
            # Продолжаем на SMTP (для надёжности)

    # Локальная отправка через SMTP (работает у тебя на компьютере)
    try:
        send_mail(
            subject='Verify your email',
            message=f'Click to verify: {verify_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"✅ Email sent via SMTP to {email}")
        return True
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False