import pandas as pd
import os
from pattern_bot.send_telegram_message import send_telegram_message
from pattern_bot.config import OPEN_TRADES_CSV
from datetime import datetime
import ccxt

def get_current_price(symbol):
    exchange = ccxt.bybit()
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']
def check_for_new_resistance():
    if not os.path.exists(OPEN_TRADES_CSV):
        return

    df = pd.read_csv(OPEN_TRADES_CSV)

    for i, row in df.iterrows():
        if pd.isna(row.get("symbol")) or pd.isna(row.get("entry")):
            continue

        symbol = row["symbol"]
        direction = row["direction"]
        entry = float(row["entry"])
        current_sl = float(row["current_sl"])
        alerted_resistance = float(row["alerted_resistance"]) if not pd.isna(row["alerted_resistance"]) else None
        current_price = get_current_price(symbol)

        # תנאים ללונג
        if direction.lower() == "long":
            new_resistance = round(current_price * 0.985, 4)  # למשל: מתחת למחיר ב-1.5%
            if alerted_resistance is None or new_resistance > alerted_resistance:
                if current_price > entry * 1.02:  # נניח התקדמות של 2%
                    new_sl = round(entry * 1.005, 4)  # להצמיד סטופ מעט מעל כניסה
                    send_telegram_message(f"""
🚨 <b>{symbol}</b> מתקרב להתנגדות חדשה!

📈 מחיר נוכחי: <b>{current_price}</b>
🟡 מומלץ לצמצם סטופ ל־<b>{new_sl}</b> כדי להגן מרווח

⏳ שעה: {datetime.now().strftime('%H:%M')}
                    """)
                    df.at[i, "alerted_resistance"] = new_resistance
                    df.at[i, "current_sl"] = new_sl

        # תנאים לשורט
        elif direction.lower() == "short":
            new_resistance = round(current_price * 1.015, 4)  # למשל: מעל ב-1.5%
            if alerted_resistance is None or new_resistance < alerted_resistance:
                if current_price < entry * 0.98:  # התקדמות שורט
                    new_sl = round(entry * 0.995, 4)  # להצמיד סטופ מעט מתחת כניסה
                    send_telegram_message(f"""
🚨 <b>{symbol}</b> מתקרב לתמיכה חזקה!

📉 מחיר נוכחי: <b>{current_price}</b>
🟡 מומלץ לצמצם סטופ ל־<b>{new_sl}</b> כדי להגן מרווח

⏳ שעה: {datetime.now().strftime('%H:%M')}
                    """)
                    df.at[i, "alerted_resistance"] = new_resistance
                    df.at[i, "current_sl"] = new_sl

    df.to_csv(OPEN_TRADES_CSV, index=False)

# פונקציה דינמית למחיר נוכחי מה־Bybit
def get_current_price(symbol):
    import requests
    base_url = "https://api.bybit.com/v5/market/tickers"
    params = {"category": "linear", "symbol": symbol}
    try:
        res = requests.get(base_url, params=params).json()
        return float(res["result"]["list"][0]["lastPrice"])
    except Exception as e:
        print(f"שגיאה בשליפת מחיר נוכחי ל־{symbol}: {e}")
        return 0