import os
import csv
import pandas as pd
from pattern_bot.config import PENDING_SIGNALS_FILE

MAX_SIGNALS_PER_RUN = 5

def save_pending_signal(symbol, timeframe, pattern, direction, entry, sl, tp, sl_pct, tp_pct, leverage, stars, duration_hr, profit_pct):
    print("📥 התחיל לבצע save_pending_signal עם הנתונים:")
    print(symbol, timeframe, pattern, direction, entry, sl, tp, sl_pct, tp_pct, leverage, stars, profit_pct, duration_hr)

    row = {
        "symbol": symbol,
        "timeframe": timeframe,
        "pattern": pattern,
        "direction": direction,
        "entry": entry,
        "stop_loss": sl,
        "take_profit": tp,
        "sl_pct": sl_pct,
        "tp_pct": tp_pct,
        "leverage": leverage,
        "stars": stars,
        "est_duration_hr": duration_hr,
        "profit_pct": profit_pct
    }
    file_exists = os.path.exists(PENDING_SIGNALS_FILE)
    print("📁 בדיקה: קיים קובץ?", file_exists)
    with open(PENDING_SIGNALS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        print("📝 כותב לקובץ עכשיו...")
        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
        print("💾 נכתב בהצלחה לקובץ PENDING_SIGNALS_FILE")
        print(f"💾 אות ממתין נשמר: {symbol} ({timeframe}) - {pattern} - ⭐ {stars} כוכבים")

def send_best_signals():
    if not os.path.exists(PENDING_SIGNALS_FILE):
        return
    df = pd.read_csv(PENDING_SIGNALS_FILE)
    if df.empty:
        return

    df_sorted = df.sort_values(by=["stars", "profit_pct"], ascending=False)
    best_signals = df_sorted.head(MAX_SIGNALS_PER_RUN)

    from pattern_bot.send_signal import send_signal

    for _, row in best_signals.iterrows():
        send_signal(
            row["symbol"],
            row["timeframe"],
            row["pattern"],
            row["direction"],
            row["entry"],
            row["stop_loss"],
            row["take_profit"],
            row["sl_pct"],
            row["tp_pct"],
            row["leverage"],
            row["stars"],
            row["est_duration_hr"],
            row["profit_pct"],
            None
        )

    os.remove(PENDING_SIGNALS_FILE)