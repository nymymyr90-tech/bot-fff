import ccxt
import pandas as pd

def get_ohlcv(symbol, timeframe='15m', limit=50):
    exchange = ccxt.bybit({'enableRateLimit': True})
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def is_volume_strong(df):
    avg_volume = df['volume'][:-1].mean()
    last_volume = df['volume'].iloc[-1]
    return last_volume > avg_volume * 1.5

def is_rsi_extreme(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]
    return latest_rsi < 30 or latest_rsi > 70