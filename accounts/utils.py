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
    print(f"[DEBUG][1] Вызов send_verification_email для {email}")
    print(f"[DEBUG][2] Переменная PYTHONANYWHERE_DOMAIN = {os.environ.get('PYTHONANYWHERE_DOMAIN')}")
    print(f"[SHOWTIME] 1. Ключ SENDGRID_API_KEY в настройках: {settings.SENDGRID_API_KEY}")
    print(f"[SHOWTIME] 2. Ключ из окружения напрямую: {os.getenv('SENDGRID_API_KEY')}")
    print(f"[SHOWTIME] 3. PYTHONANYWHERE_DOMAIN из окружения: {os.getenv('PYTHONANYWHERE_DOMAIN')}")
    print(f"[SHOWTIME] 4. Весь os.environ содержит PYTHONANYWHERE_DOMAIN?: {'PYTHONANYWHERE_DOMAIN' in os.environ}")
    # Проверяем, находимся ли на PythonAnywhere
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:  # Более надёжный способ
        print(f"[DEBUG][3] Условие 'PYTHONANYWHERE_DOMAIN in os.environ' = ИСТИНА. Использую SendGrid API.")
        try:
            return send_email_via_sendgrid_api(email, token)
        except python_http_client.exceptions.UnauthorizedError as e:
            # ⬇️ ВОТ ЭТО ДОБАВЬ ⬇️
            print(f"❌ SendGrid 401. Тело ответа: {e.body}")
            # Может быть ещё статус и заголовки
            print(f"Status: {e.status_code}, Headers: {e.headers}")
            return False
        except ImportError as e:
            print(f"⚠️ [DEBUG][4] Cannot import SendGrid helper: {e}")
            # Продолжаем на SMTP (для надёжности)
        except Exception as e:
            print(f"⚠️ [DEBUG][5] Неизвестная ошибка в send_email_via_sendgrid_api: {e}")
            # Продолжаем на SMTP (для надёжности)

    print(f"[DEBUG][6] Использую запасной путь: SMTP.")
    # Локальная отправка через SMTP (работает у тебя на компьютере)
    try:
        send_mail(
            subject='Verify your email',
            message=f'Click to verify: {verify_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"✅ [DEBUG][7] Email sent via SMTP to {email}")
        return True
    except Exception as e:
        print(f"❌ [DEBUG][8] Email send failed: {e}")
        return False


def get_max_gallery_avatars(score: int) -> int:
    if score >= 25000:
        return 3
    elif score >= 10000:
        return 2
    elif score >= 5000:
        return 1
    return 0