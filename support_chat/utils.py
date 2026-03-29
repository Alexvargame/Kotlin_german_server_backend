import firebase_admin
from firebase_admin import credentials, messaging

# Инициализация (выполнить один раз при старте сервера)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  # путь к вашему ключу
    firebase_admin.initialize_app(cred)

def send_push(fcm_token: str, title: str, body: str, data: dict = None):
    """
    Отправка push-уведомления на устройство.

    :param token: FCM-токен устройства
    :param title: заголовок уведомления
    :param body: текст уведомления
    :param data: словарь с дополнительными данными (необязательно)
    :return: ответ FCM или None в случае ошибки
    """
    print('SEND_PUSH', fcm_token, title, body, data)
    # Собираем сообщение
    message = messaging.Message(
        token=fcm_token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {}  # если data не передан, будет пустой словарь
    )
    print("Message", message)
    try:
        response = messaging.send(message)
        print(f"[OK] Уведомление отправлено: {response}")
        return response
    except Exception as e:
        print(f"[ERROR] Не удалось отправить: {e}")
        # Здесь можно обработать специальные ошибки (например, UnregisteredError)
        return None