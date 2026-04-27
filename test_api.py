import requests

BASE_URL = "http://127.0.0.1:8080"

# Создаем сессию, чтобы куки (авторизация) сохранялись между запросами
session = requests.Session()

# 1. Пробуем войти
login_data = {
    "email": "твоя_почта@mail.ru",
    "password": "твой_пароль"
}
print("Attempting to log in...")
response = session.post(f"{BASE_URL}/api/login", json=login_data)
print("Status Code:", response.status_code)
print("Content Type:", response.headers.get('Content-Type'))
if response.status_code == 200:
    print("Login:", response.json())
else:
    print("Full Response:", response.text)

# 2. Если вход успешен, заказываем еду
if response.status_code == 200:
    order_data = {"item": "Биг Спешиал"}
    order_res = session.post(f"{BASE_URL}/api/order", json=order_data)
    print("Order Status:", order_res.json())