import os
import sys
import json
import ccxt
import pandas as pd
from datetime import datetime

# חיבור לתיקיית pattern_bot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pattern_bot')))

# הגדרת הבורסה
exchange = ccxt.bybit()

# תיקייה לשמירת הקבצים
SAVE_DIR = os.path.join(os.path.dirname(__file__), "historical_patterns")
os.makedirs(SAVE_DIR, exist_ok=True)

# משיכת נתונים
def get_ohlcv(symbol, timeframe='15m', limit=100):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception as e:
        print(f"שגיאה בהבאת נתונים עבור {symbol}: {e}")
        return None

# שמירת תבנית אחת
def save_pattern(symbol, timeframe='15m', length=30):
    print(f"🔄 שומר תבנית עבור {symbol}")
    df = get_ohlcv(symbol, timeframe)
    if df is None or len(df) < length:
        print(f"⚠ אין מספיק נתונים עבור {symbol}")
        return

    pattern_data = df[-length:][['close']].reset_index(drop=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    safe_symbol = symbol.replace("/", "_")
    filename = f"{safe_symbol}_{timestamp}.json"
    filepath = os.path.join(SAVE_DIR, filename)

    pattern_data.to_json(filepath, orient='records', indent=2)
    print(f"✅ נשמר בהצלחה {symbol} בקובץ {filename}")

# ריצה על כל הסימבולים
if __name__ == "__main__":
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'pattern_bot', 'symbols.json'), "r", encoding="utf-8") as f:
            symbols = json.load(f)
    except Exception as e:
        print(f"⚠ שגיאה בקריאת symbols.json: {e}")
        symbols = []

    for symbol in symbols:
        print(f"\n🔍 מריץ שמירה עבור {symbol}")
        save_pattern(symbol)