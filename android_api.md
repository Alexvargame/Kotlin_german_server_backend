# 📱 API для Android — German Backend
Документация JSON request/response для Android-разработчиков. Все токены (email_token и login_token) подставляются автоматически в Postman.

## 1️⃣ Register (Регистрация)
- Метод: POST  
- URL: /api/register/
- Body (JSON):
{
  "email": "example@test.com",
  "password": "12345678"
}
- Response (JSON):
{
  "uid": "819d3ffe-478b-45b2-be3a-563ded68c4d1",
  "message": "Verification email sent",
  "email_token": "438a5dfd-9680-4ed6-b8b2-967cecaba269"
}
- Описание: Создаёт пользователя и генерирует токен для подтверждения email (email_token).

## 2️⃣ Login (Вход)
- Метод: POST  
- URL: /api/login/
- Body (JSON):
{
  "email": "example@test.com",
  "password": "12345678"
}
- Response (JSON):
{
  "uid": "819d3ffe-478b-45b2-be3a-563ded68c4d1",
  "token": "2760e10891b0b2ea6b059e3e2366cbb52ef70d3c"
}
- Описание: Логин пользователя. Создаётся login_token, который используется для авторизации последующих запросов.

## 3️⃣ Profile (Профиль пользователя)
- Метод: GET  
- URL: /api/profile/  
- Header: Authorization: Token {{login_token}}
- Response (JSON):
{
  "uid": "819d3ffe-478b-45b2-be3a-563ded68c4d1",
  "email": "example@test.com",
  "is_verified": false
}
- Описание: Получение данных профиля пользователя. Требуется токен авторизации (login_token).

## 4️⃣ Verify Email (Подтверждение email)
- Метод: GET  
- URL: /api/verify-email/?token={{email_token}}  
- Header (если требуется): Authorization: Token {{login_token}}
- Response (JSON):
{
  "message": "Email verified successfully"
}
- Описание: Подтверждает email пользователя. Использует токен email_token, полученный после регистрации.

## ✅ Итого
- email_token → для /api/verify-email/  
- login_token → для Authorization в /api/profile/  
- Примеры JSON полностью готовы к использованию Android-разработчиками. Можно сразу копировать и вставлять в Postman / Android код.
