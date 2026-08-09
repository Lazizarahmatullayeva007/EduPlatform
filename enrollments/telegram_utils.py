import requests
from django.conf import settings


def send_telegram_message(text):
    """
    Telegram Bot API orqali xabar yuboradi.
    Agar .env da token/chat_id sozlanmagan bo'lsa, konsolga chiqarib qo'yadi
    (development muhitida xato bermasligi uchun).
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print(f"[TELEGRAM XABAR YUBORILMADI - sozlanmagan] {text}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=5)
        if response.status_code != 200:
            print(f"[TELEGRAM XATO] {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"[TELEGRAM ULANISH XATOSI] {e}")