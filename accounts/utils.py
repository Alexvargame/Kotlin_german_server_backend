# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings
import os
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

    # Если на сервере - используем SendGrid API
    if 'pythonanywhere.com' in os.environ.get('SERVER_HOSTNAME', ''):
        try:
            from .sendgrid_helper import send_email_via_sendgrid_api
            return send_email_via_sendgrid_api(email, token)
        except ImportError:
            pass  # Упадём на локальный вариант

    # Локально - обычный SMTP (работает как раньше)
    send_mail(
        subject='Verify your email',
        message=f'Click to verify: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    print(f"✅ Email sent via SMTP to {email}")
    return True