import ccxt, time, pandas as pd, os, pytz, schedule, matplotlib.pyplot as plt, requests
import csv
from datetime import datetime
from pattern_bot.statistics_report import send_weekly_and_monthly_report
from pattern_bot.resistance_monitor import check_for_new_resistance
from pattern_bot.charting.generate_chart import generate_trade_chart
from pattern_bot.send_signal import send_signal
from pattern_bot.send_message import send_telegram_message, send_telegram_message_with_image, send_signal
from pattern_bot.send_error_alert import send_error_alert
from pattern_bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_USER, TELEGRAM_CHAT_ID_GROUP, OPEN_TRADES_CSV, SIGNALS_LOG_FILE, PENDING_SIGNALS_FILE
from pattern_bot.detect_candlestick_patterns import detect_candlestick_pattern
from pattern_bot.rating import get_star_rating
from graph_pattern_matching.compare_graph_patterns import match_current_pattern
from pattern_bot.send_pending_signal import save_pending_signal, send_best_signals
from pattern_bot.config import OPEN_TRADES_CSV
from pattern_bot.ai_predictor import (
    predict_success_probability, final_ai_decision,
    check_volume_support, check_rsi_confirmation,
    check_price_stability, check_btc_correlation,
    evaluate_pattern_confidence, ai_ensemble_decision
)

def get_leverage_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info?category=linear"
    r = requests.get(url)
    data = r.json()
    return [i['symbol'] for i in data['result']['list'] if i.get('status') == 'Trading']

TIMEFRAMES = ['15m', '1h', '4h']
LIMIT = 100
MAX_SIGNALS_PER_RUN = 5
exchange = ccxt.bybit({'enableRateLimit': True})

if not os.path.exists(SIGNALS_LOG_FILE):
    pd.DataFrame(columns=[
        "symbol", "timeframe", "timestamp", "pattern", "direction",
        "entry", "stop_loss", "take_profit", "sl_pct", "tp_pct",
        "leverage", "stars", "est_duration_hr", "profit_pct"
    ]).to_csv(SIGNALS_LOG_FILE, index=False)

def generate_chart(df, entry, sl, tp, direction, symbol):
    plt.figure(figsize=(10, 4))
    plt.plot(df['timestamp'], df['close'], label='Close', color='black')
    plt.axhline(entry, color='blue', linestyle='--', label='Entry')
    plt.axhline(sl, color='red', linestyle='--', label='Stop Loss')
    plt.axhline(tp, color='green', linestyle='--', label='Take Profit')
    forecast = [entry + (tp - entry) * i / 10 if direction == 'bullish' else entry - (entry - tp) * i / 10 for i in range(11)]
    forecast_x = [df['timestamp'].iloc[-1] + pd.Timedelta(minutes=15*i) for i in range(11)]
    plt.plot(forecast_x, forecast, linestyle=':', color='orange', label='Forecast')
    plt.title(f"{symbol} Forecast")
    plt.legend()
    plt.tight_layout()
    chart_path = 'chart.png'
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def calculate_levels(df, direction):
    close = df['close'].iloc[-1]
    atr = df['high'].rolling(5).max().iloc[-1] - df['low'].rolling(5).min().iloc[-1]
    sl = close - atr if direction == 'bullish' else close + atr
    tp = close + atr * 2 if direction == 'bullish' else close - atr * 2
    sl_pct = round(abs((close - sl) / close) * 100, 2)
    tp_pct = round(abs((tp - close) / close) * 100, 2)
    if sl_pct < 0.3 or sl_pct > 4.5 or tp_pct < 0.6:
        print(f"⛔ אות נפסל – SL: {sl_pct}%, TP: {tp_pct}%")
        return None
    leverage = 30 if sl_pct <= 0.5 else 20 if sl_pct <= 1 else 15 if sl_pct <= 2 else 10
    profit_pct = round(tp_pct * leverage, 2)
    est_duration_hr = 1 if df.shape[0] < 30 else round(df.shape[0] * 0.25)
    return round(close, 6), round(sl, 6), round(tp, 6), sl_pct, tp_pct, leverage, profit_pct, est_duration_hr

import csv

def save_pending_signal(symbol, timeframe, pattern, direction, entry, sl, tp, sl_pct, tp_pct, leverage, stars, duration_hr, profit_pct):
    row = {
        "symbol": symbol, "timeframe": timeframe, "pattern": pattern,
        "direction": direction, "entry": entry, "stop_loss": sl,
        "take_profit": tp, "sl_pct": sl_pct, "tp_pct": tp_pct,
        "leverage": leverage, "stars": stars, "est_duration_hr": duration_hr,
        "profit_pct": profit_pct
    }
    file_exists = os.path.exists(PENDING_SIGNALS_FILE)
    with open(PENDING_SIGNALS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def send_best_signals():
    if not os.path.exists(PENDING_SIGNALS_FILE):
        return
    df = pd.read_csv(PENDING_SIGNALS_FILE)
    if df.empty:
        return
    df_sorted = df.sort_values(by=["stars", "profit_pct"], ascending=False)
    best_signals = df_sorted.head(MAX_SIGNALS_PER_RUN)
    for _, row in best_signals.iterrows():
        send_signal(
            row['symbol'], row['timeframe'], row['pattern'], row['direction'],
            row['entry'], row['stop_loss'], row['take_profit'],
            row['sl_pct'], row['tp_pct'], row['leverage'],
            row['stars'], row['est_duration_hr'], row['profit_pct'], None
        )
    os.remove(PENDING_SIGNALS_FILE)

def run():
    try:
        print(f"🚀 התחלת סריקה: {datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%H:%M:%S')}")
        symbols = get_leverage_symbols()
        signal_count = 0
        for symbol in symbols:
            for tf in TIMEFRAMES:
                try:
                    print(f"🔍 סריקה: {symbol} ({tf})")
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=LIMIT)
                    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                    # Candlestick
                    candle = detect_candlestick_pattern(df)
                    if candle and candle.get('name') and candle.get('direction'):
                        direction = candle['direction']
                        if is_valid_daily_trend(symbol, direction):
                            res = calculate_levels(df, direction)
                            if res:
                                entry, sl, tp, sl_pct, tp_pct, lev, profit_pct, duration_hr = res
                                stars = get_star_rating(candle['name'], symbol, tf, True)
                                print(f"🔦 נר {candle['name']} ({symbol} - {tf}) → כוכבים: {stars}")
                                if (stars >= 5 or (stars == 4 and signal_count == 0)) and signal_count < MAX_SIGNALS_PER_RUN:
                                    prob = predict_success_probability(tp_pct, sl_pct, tf, stars, direction)
                                    v = check_volume_support(df, direction)
                                    r = check_rsi_confirmation(df, direction)
                                    s = check_price_stability(df)
                                    b = check_btc_correlation(symbol, direction)
                                    p = evaluate_pattern_confidence(candle['name'])
                                    print("📊 בדיקת AI: ", f"prob={prob:.2f}", f"v={v}", f"r={r}", f"s={s}", f"b={b}", f"p={p}")
                                    if stars >= 4:
                                        save_pending_signal(
                                            symbol, tf, candle['name'], direction, entry, sl, tp,
                                            sl_pct, tp_pct, lev, stars, duration_hr, profit_pct
                                        )
                                    if ai_ensemble_decision(prob, v, r, s, b, p):
                                        print(f"✅ עבר AI...")
                                        pattern = candle['name']
                                        send_signal(
                                            symbol, tf, candle['name'], direction, entry, sl, tp,
                                            sl_pct, tp_pct, lev, stars, duration_hr, profit_pct
                                        )
                                        signal_count += 1
                                        check_for_new_resistance()
                                    else:
                                        print(f"❌ לא עבר AI ❌ - {symbol} ({tf}) - {candle['name']} - ⭐ {stars}")

                    pattern_name, direction, stars = match_current_pattern(df)
                    if pattern_name and direction:
                        print(f"📊 תבנית {pattern_name} ({symbol} - {tf}) → כוכבים: {stars}")
                        if stars >= 4 and is_valid_daily_trend(symbol, direction):
                            res = calculate_levels(df, direction)
                            if res:
                                entry, sl, tp, sl_pct, tp_pct, lev, profit_pct, duration_hr = res
                                prob = predict_success_probability(tp_pct, sl_pct, tf, stars, direction)
                                v = check_volume_support(df, direction)
                                r = check_rsi_confirmation(df, direction)
                                s = check_price_stability(df)
                                b = check_btc_correlation(symbol, direction)
                                p = evaluate_pattern_confidence(pattern_name)
                                # שמירה של כל העסקאות עם 4 כוכבים ומעלה
                            if stars >= 4:
                                save_pending_signal(symbol, tf, pattern_name, direction, entry, sl, tp,
                                                    sl_pct, tp_pct, lev, stars, duration_hr, profit_pct)

                                # שליחה רק אם AI מאשר
                            if ai_ensemble_decision(prob, v, r, s, b, p):
                                send_signal(symbol, tf, pattern_name, direction, entry, sl, tp, sl_pct, tp_pct,
                                            lev, stars, duration_hr, profit_pct)
                                signal_count += 1
                                check_for_new_resistance()
                    
                except Exception as e:
                    err = f"שגיאה בסריקה עבור {symbol} ({tf}):\n{type(e).__name__}: {e}"
                    print(err)
                    send_error_alert(err)
    except Exception as e:
        err = f"שגיאה כללית בבוט הראשי: {type(e).__name__}: {e}"
        print(err)
        send_error_alert(err)

def send_daily_report():
    try:
        if not os.path.exists(SIGNALS_LOG_FILE): return
        df = pd.read_csv(SIGNALS_LOG_FILE)
        today = datetime.now(pytz.timezone('Asia/Jerusalem')).strftime('%Y-%m-%d')
        df_today = df[df['timestamp'].str.startswith(today)]
        count = len(df_today)
        avg_profit = df_today['profit_pct'].mean() if count > 0 else 0
        msg = f"📊 דוח יומי {today}:\n📈 סה\"כ עסקאות: {count}\n💰 רווח ממוצע: {round(avg_profit, 2)}%"
        send_telegram_message_with_image(msg, None)
    except Exception as e:
        print(f"שגיאה בשליחת דוח יומי: {e}")

def is_valid_daily_trend(symbol, direction):
    return True  # להשלמה בעתיד

if __name__ == "__main__":
    send_telegram_message_with_image("כמה דקות וממשיכים..", None)
    schedule.every().day.at("23:59").do(send_daily_report)
    schedule.every().saturday.at("23:59:30").do(send_weekly_and_monthly_report)
    schedule.every().day.at("00:00").do(lambda: send_weekly_and_monthly_report() if datetime.now().day == 1 else None)
    while True:
        run()
        send_best_signals()
        schedule.run_pending()
        print("🕒 ממתין 15 דקות...\n")
        time.sleep(60 * 15)