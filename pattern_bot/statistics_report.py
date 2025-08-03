import pandas as pd
from datetime import datetime, timedelta
from pattern_bot.send_message import send_telegram_message_with_image
from pattern_bot.send_error_alert import send_error_alert

def send_weekly_and_monthly_report():
    try:
        df = pd.read_csv('closed_trades.csv')  # אפשר לשנות ל־config אם קיים
        df['closed_at'] = pd.to_datetime(df['closed_at'])

        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1)

        df_week = df[df['closed_at'] >= start_of_week]
        df_month = df[df['closed_at'] >= start_of_month]

        def build_stats(df_period, title):
            if df_period.empty:
                return f"{title}:\nאין נתונים לתקופה הזאת."
            total = len(df_period)
            wins = len(df_period[df_period['result'] == 'win'])
            losses = len(df_period[df_period['result'] == 'loss'])
            avg_pnl = df_period['pnl_percent'].mean()
            win_rate = (wins / total) * 100
            return (
                f"📊 {title}\n"
                f"• עסקאות: {total}\n"
                f"• הצלחות: {wins} ✅\n"
                f"• כשלונות: {losses} ❌\n"
                f"• אחוז הצלחה: {win_rate:.1f}%\n"
                f"• רווח ממוצע: {avg_pnl:.2f}%\n"
            )

        # שליחה אם זה מוצ״ש
        if now.weekday() == 6 and now.hour == 23:
            msg = build_stats(df_week, "דו\"ח שבועי")
            send_telegram_message_with_image(msg, None)

        # שליחה אם זה היום הראשון בחודש
        if now.day == 1 and now.hour == 23:
            msg = build_stats(df_month, "דו\"ח חודשי")
            send_telegram_message_with_image(msg, None)

    except Exception as e:
        send_error_alert(f"שגיאה בדו\"ח סטטיסטיקה: {e}")