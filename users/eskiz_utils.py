import requests
from django.conf import settings


def get_eskiz_token():
    """
    Eskiz.uz email+parol orqali login qilib, vaqtinchalik token oladi.
    Bu token keyin SMS yuborishda ishlatiladi.
    """
    email = settings.ESKIZ_EMAIL
    password = settings.ESKIZ_PASSWORD

    if not email or not password:
        return None

    url = "https://notify.eskiz.uz/api/auth/login"
    try:
        response = requests.post(url, data={"email": email, "password": password}, timeout=5)
        if response.status_code == 200:
            return response.json()["data"]["token"]
    except requests.RequestException:
        pass
    return None


def send_sms(phone_number, message):
    """
    Eskiz.uz orqali SMS yuboradi.
    Agar ESKIZ_EMAIL/PASSWORD sozlanmagan bo'lsa, konsolga chiqarib qo'yadi
    (development muhitida xato bermasligi uchun).
    """
    token = get_eskiz_token()

    if not token:
        print(f"[SMS YUBORILMADI - Eskiz sozlanmagan] {phone_number} ga: {message}")
        return

    url = "https://notify.eskiz.uz/api/message/sms/send"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "mobile_phone": phone_number,
        "message": message,
        "from": "4546",
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=5)
        if response.status_code != 200:
            print(f"[SMS XATOSI] {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"[SMS ULANISH XATOSI] {e}")