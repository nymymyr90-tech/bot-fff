import requests
import pandas as pd

def get_btc_data(timeframe='1h'):
    url = f'https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval={timeframe}&limit=200'
    try:
        response = requests.get(url)
        data = response.json()
        if 'result' not in data or 'list' not in data['result']:
            return None
        raw = data['result']['list']
        df = pd.DataFrame(raw, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)

        # ניתן להוסיף אלטים עתידית אם רוצים לבדוק קורלציה אמיתית
        df['altcoins'] = {'ETHUSDT': df['close'] * 0.98}  # דמה

        return df
    except Exception as e:
        print(f"שגיאה בשליפת נתוני BTC: {str(e)}")
        return None