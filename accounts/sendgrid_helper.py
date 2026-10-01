import logging

import python_http_client
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

def send_email_via_sendgrid_api(email, token):
    """
    Отправка письма через SendGrid API (для PythonAnywhere Free).
    """
    print(f"[DEBUG-SendGrid][A] Функция send_email_via_sendgrid_api вызвана для {email}")
    verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'
    # Формируем письмо
    print(f"[DEBUG-SendGrid][B] Формирую письмо...")
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject='Verify your email',
        html_content=f'Click to verify: <a href="{verify_url}">{verify_url}</a>'
    )

    # Отправляем через API
    try:
        print(f"[DEBUG-SendGrid][C] Пытаюсь создать клиент SendGrid с ключём: {settings.SENDGRID_API_KEY[:10]}...")
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        print(f"[DEBUG-SendGrid][D] Клиент создан. Пытаюсь отправить письмо...")
        response = sg.send(message)
        print(f"[DEBUG-SendGrid][E] ✅ Отправка через API успешна! Статус: {response.status_code}")
        return True
    except python_http_client.exceptions.UnauthorizedError as e:
        # 👇 Здесь будет тело ответа с причиной
        print(f"[DEBUG-SendGrid][F] ❌ 401 Unauthorized. Тело ответа: {e.body}")
        print(f"Статус: {e.status_code}, Заголовки: {e.headers}")
        return False
    except Exception as e:
        print(f"[DEBUG-SendGrid][F] ❌ КРИТИЧЕСКАЯ ОШИБКА в SendGrid API: {e}")
        return False


def send_email_via_brevo_api(email, token):
    """Отправка письма через Brevo API (для PythonAnywhere Free)."""
    print(f"[DEBUG-Brevo][A] Функция send_email_via_brevo_api вызвана для {email}")
    verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = {"name": "German App", "email": settings.DEFAULT_FROM_EMAIL}
    to = [{"email": email}]
    subject = "Verify your email"
    html_content = f'Click to verify: <a href="{verify_url}">{verify_url}</a>'

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"[DEBUG-Brevo][E] ✅ Отправка успешна")
        return True
    except ApiException as e:
        print(f"[DEBUG-Brevo][F] ❌ Ошибка: {e}")
        return False