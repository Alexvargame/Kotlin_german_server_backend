import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()
api_key = os.getenv('SENDGRID_API_KEY')
print(f'DEBUG: Ключ получен? {api_key is not None}')

message = Mail(
    from_email='a_odegov@ukr.net',
    to_emails='ВАШ_РЕАЛЬНЫЙ_EMAIL@gmail.com',  # Замените на свой email
    subject='Тест SendGrid из скрипта',
    plain_text_content='Если вы это читаете, SendGrid работает.'
)

try:
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    print(f'УСПЕХ! Код: {response.status_code}')
except Exception as e:
    print(f'ОШИБКА: {e}')