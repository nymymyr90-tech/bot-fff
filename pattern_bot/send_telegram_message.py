import os
import requests
from pattern_bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_USER, TELEGRAM_CHAT_ID_GROUP

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in [TELEGRAM_CHAT_ID_USER, TELEGRAM_CHAT_ID_GROUP]:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ שגיאה בשליחת הודעה טקסט ({chat_id}): {e}")

def send_telegram_message_with_image(message, image_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    for chat_id in [TELEGRAM_CHAT_ID_USER, TELEGRAM_CHAT_ID_GROUP]:
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img:
                    files = {'photo': img}
                    data = {'chat_id': chat_id, 'caption': message, 'parse_mode': 'HTML'}
                    response = requests.post(url, files=files, data=data)
                    response.raise_for_status()
            else:
                send_telegram_message(message)
        except Exception as e:
            print(f"❌ שגיאה בשליחת הודעה עם תמונה ({chat_id}): {e}")