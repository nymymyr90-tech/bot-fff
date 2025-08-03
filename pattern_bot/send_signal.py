import os
import csv
from telegram import Bot
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_USER, TELEGRAM_CHAT_ID_GROUP
from .send_telegram_message import send_telegram_message, send_telegram_message_with_image
from .charting.generate_chart import generate_trade_chart

def send_signal(symbol, tf, pattern_name, direction, entry, sl, tp,
                tp_pct=25.0, sl_pct=25.0, leverage=10, stars=5,
                duration_hr=1.5, profit_pct=None, df=None):
    # יצירת גרף אם df קיים
    image_path = None
    if df is not None:
        try:
            image_path = generate_trade_chart(df, symbol, direction, entry, sl, tp)
        except Exception as e:
            print(f"שגיאה ביצירת גרף: {e}")

    # הכנת ההודעה המלאה
    star_text = f"{'⭐' * stars}"
    direction_arrow = "📈" if direction == "bullish" else "📉"
    sl_line = f"🛡 סטופ: {sl} ({sl_pct:.1f}%)"
    tp_line = f"🎯 טייק: {tp} ({tp_pct:.1f}%)"
    pattern_line = f"{direction_arrow} תבנית: {pattern_name}"

    message = (
        f"📊 <b>איתות חדש</b> ({star_text})\n"
        f"<b>{symbol}</b>\n"
        f"⏱ טיים פריים: {tf}\n"
        f"{pattern_line}\n"
        f"🎯 כניסה: {entry}\n"
        f"{sl_line}\n"
        f"{tp_line}\n"
        f"💥 מינוף: x{leverage}\n"
        f"⏳ זמן משוער: {duration_hr} שעות\n"
        f"💰 רווח צפוי: {profit_pct:.1f}%"
    )

    print(f"📤 שולח איתות: {symbol}, {tf}, {pattern_name}, ⭐ {stars}")

    # שליחה לטלגרם
    try:
        if image_path and os.path.exists(image_path):
            send_telegram_message_with_image(message, image_path)
            send_telegram_message_with_image(message, image_path, chat_id=TELEGRAM_CHAT_ID_GROUP)
        else:
            send_telegram_message(message)
            send_telegram_message(message, chat_id=TELEGRAM_CHAT_ID_GROUP)
    except Exception as e:
        print(f"שגיאה בשליחת טלגרם: {e}")

    # שמירת העסקה כעסקה פתוחה
    save_open_trade(symbol, tf, direction, entry, sl, tp)

def save_open_trade(symbol, tf, direction, entry, sl, tp):
    file_path = "open_trades.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "symbol", "timeframe", "direction",
                "entry", "stop_loss", "take_profit",
                "current_sl", "alerted_resistance"
            ])
        writer.writerow([symbol, tf, direction, entry, sl, tp, sl, ""])