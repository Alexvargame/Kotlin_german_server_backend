import requests

print("🔥🔥🔥 SYNC VIEW EXECUTED 1111🔥🔥🔥")
# --- Настройки ---
url = "http://127.0.0.1:8000/api/upload-gallery-avatar/"  # URL сервера
token = "b1aef66cd5c682971246a19b2f8f7503b9b8473d"
uid = "415d8b8f-a3a5-47a6-a202-a586b3960c07"
avatar_last_changed = "1672531200"
file_path = "avatars_1.jpg"  # путь к файлу для загрузки

# --- Заголовки ---
headers = {
    "Authorization": f"Token {token}"
}

# --- Файлы и данные ---
files = {
    "image": open(file_path, "rb")
}
data = {
    "uid": uid,
    "avatar_last_changed": avatar_last_changed
}

# --- POST запрос ---
response = requests.post(url, headers=headers, files=files, data=data)
print("🔥🔥🔥 SYNC VIEW EXECUTED222 🔥🔥🔥")
print("Status code:", response.status_code)
print("Status:", response.status_code)
print("Raw response:")
print(response.text)