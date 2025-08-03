def detect_candlestick_pattern(df):
    if len(df) < 3:
       # Morning Star
     if len(df) >= 3:
        a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (
            a['close'] < a['open'] and  # נר ראשון אדום
            abs(b['close'] - b['open']) < (a['open'] - a['close']) * 0.5 and  # נר שני קטן (דוג'י)
            c['close'] > c['open'] and
            c['close'] > (a['open'] + a['close']) / 2  # נר שלישי עובר חצי מגוף הראשון
        ):
            return {'name': 'Morning Star', 'direction': 'bullish'}

    # Evening Star
    if len(df) >= 3:
        a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (
            a['close'] > a['open'] and  # נר ראשון ירוק
            abs(b['close'] - b['open']) < (a['close'] - a['open']) * 0.5 and  # נר שני קטן (דוג'י)
            c['close'] < c['open'] and
            c['close'] < (a['open'] + a['close']) / 2  # נר שלישי יורד מתחת לחצי מהראשון
        ):
            return {'name': 'Evening Star', 'direction': 'bearish'}    
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]

    o, h, l, c = last['open'], last['high'], last['low'], last['close']
    body = abs(c - o)
    candle_range = h - l

    # Hammer
    if body < candle_range * 0.3 and (min(o, c) - l) > body * 2 and (h - max(o, c)) < body * 0.5:
        direction = 'bullish' if c > o else 'bearish'
        return {'name': 'Hammer', 'direction': direction}

    # Inverted Hammer
    if body < candle_range * 0.3 and (h - max(o, c)) > body * 2 and (min(o, c) - l) < body * 0.5:
        return {'name': 'Inverted Hammer', 'direction': 'bullish'}

    # Shooting Star
    if body < candle_range * 0.3 and (h - max(o, c)) > body * 2 and (min(o, c) - l) < body * 0.5:
        return {'name': 'Shooting Star', 'direction': 'bearish'}

    # Doji
    if body <= candle_range * 0.1:
        return {'name': 'Doji', 'direction': 'neutral'}

    # Bullish Engulfing
    if (
        prev['close'] < prev['open'] and
        c > o and
        c > prev['open'] and
        o < prev['close']
    ):
        return {'name': 'Bullish Engulfing', 'direction': 'bullish'}

    # Bearish Engulfing
    if (
        prev['close'] > prev['open'] and
        c < o and
        c < prev['open'] and
        o > prev['close']
    ):
        return {'name': 'Bearish Engulfing', 'direction': 'bearish'}

    # Morning Star (3 candles)
    if (
        prev2['close'] < prev2['open'] and  # red
        abs(prev['close'] - prev['open']) < candle_range * 0.2 and  # small body
        last['close'] > prev2['open']  # strong green
    ):
        return {'name': 'Morning Star', 'direction': 'bullish'}

    # Evening Star (3 candles)
    if (
        prev2['close'] > prev2['open'] and  # green
        abs(prev['close'] - prev['open']) < candle_range * 0.2 and  # small body
        last['close'] < prev2['open']  # strong red
    ):
        return {'name': 'Evening Star', 'direction': 'bearish'}

    return None