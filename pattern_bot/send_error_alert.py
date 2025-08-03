from telegram import Bot
from pattern_bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_USER
import asyncio

def send_error_alert(error_msg):
    try:
        message = f"❗ באיתות שגיאה:\n{error_msg}"
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        # הרצת השליחה בצורה אסינכרונית
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID_USER, text=message))

    except Exception as e:
        print(f"שגיאה בשליחת הודעת שגיאה: {e}")