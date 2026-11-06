import logging

import python_http_client
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

# def send_email_via_brevo_api(email, token):
#     """Отправка письма через Brevo API (для PythonAnywhere Free)."""
#     print(f"[DEBUG-Brevo][A] Функция send_email_via_brevo_api вызвана для {email}")
#     verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'
#
#     configuration = sib_api_v3_sdk.Configuration()
#     configuration.api_key['api-key'] = settings.BREVO_API_KEY
#
#     api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
#         sib_api_v3_sdk.ApiClient(configuration)
#     )
#
#     sender = {"name": "German App", "email": settings.DEFAULT_FROM_EMAIL}
#     to = [{"email": email}]
#     subject = "Verify your email"
#     html_content = f'Click to verify: <a href="{verify_url}">{verify_url}</a>'
#
#     send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#         to=to,
#         sender=sender,
#         subject=subject,
#         html_content=html_content
#     )
#
#     try:
#         api_instance.send_transac_email(send_smtp_email)
#         print(f"[DEBUG-Brevo][E] ✅ Отправка успешна")
#         return True
#     except ApiException as e:
#         print(f"[DEBUG-Brevo][F] ❌ Ошибка: {e}")
#         return False

import requests


def send_email_via_brevo_api(email, token):
    verify_url = f'https://alexdirect.pythonanywhere.com/api/verify-email/?token={token}'

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "sender": {"email": settings.DEFAULT_FROM_EMAIL},
            "to": [{"email": email}],
            "subject": "Verify your email",
            "htmlContent": f'Click to verify: <a href="{verify_url}">{verify_url}</a>'
        }
    )

    if response.status_code == 201:
        return True
    print(f"Brevo error: {response.status_code} {response.text}")
    return False
