import logging
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

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
    except Exception as e:
        print(f"[DEBUG-SendGrid][F] ❌ КРИТИЧЕСКАЯ ОШИБКА в SendGrid API: {e}")
        return False