import pandas as pd
import numpy as np

def match_current_pattern(df):
    if len(df) < 20:
        return None, None, None

    closes = df['close'].values
    norm = (closes - np.min(closes)) / (np.max(closes) - np.min(closes))

    stars = 0

    # תבנית W
    if (
        norm[-5] < norm[-4] and
        norm[-4] > norm[-3] and
        norm[-3] < norm[-2] and
        norm[-2] > norm[-1]
    ):
        stars = 5
        return "W pattern", "bullish", stars

    # תבנית M
    if (
        norm[-5] > norm[-4] and
        norm[-4] < norm[-3] and
        norm[-3] > norm[-2] and
        norm[-2] < norm[-1]
    ):
        stars = 5
        return "M pattern", "bearish", stars

    # תבנית Bullish חזקה (נר אחד)
    last_candle = df.iloc[-1]
    if last_candle['close'] > last_candle['open'] * 1.021:
        stars = 4
        return "Strong Bullish", "bullish", stars

    # תבנית Bearish חזקה (נר אחד)
    if last_candle['close'] < last_candle['open'] * 0.98:
        stars = 4
        return "Strong Bearish", "bearish", stars

    return None, None, None