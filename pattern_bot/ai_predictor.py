import numpy as np
import pandas as pd
from pattern_bot.data_sources import get_btc_data, get_coin_data

def predict_success_probability(tp_pct, sl_pct, tf, stars, direction):
    risk_reward = tp_pct / sl_pct if sl_pct > 0 else 0
    tf_weight = {'15m': 1.0, '1h': 1.1, '4h': 1.2}.get(tf, 1.0)
    score = (stars * 10 + risk_reward * 20) * tf_weight
    return min(100, round(score, 2))

def final_ai_decision(probability, min_threshold=70):
    return probability >= min_threshold

def check_volume_support(df, direction):
    recent_vol = df['volume'].iloc[-10:].mean()
    prev_vol = df['volume'].iloc[-20:-10].mean()
    return recent_vol > prev_vol

def check_rsi_confirmation(df, direction):
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if direction == 'bullish':
        return latest_rsi < 70
    else:
        return latest_rsi > 30

def check_price_stability(df, threshold=3.0):
    std_dev = df['close'].pct_change().std() * 100
    return std_dev < threshold

def check_btc_correlation(symbol, direction, timeframe='1h'):
    try:
        df_symbol = get_coin_data(symbol, timeframe)
        df_btc = get_btc_data(timeframe)

        if df_symbol is None or df_btc is None:
            return False

        df = pd.merge(df_symbol, df_btc, on='timestamp', suffixes=('', '_btc'))
        if len(df) < 10:
            return False

        correlation = df['close'].corr(df['close_btc'])
        if direction == 'bullish':
            return correlation > 0.3
        else:
            return correlation < -0.3
    except:
        return False

def check_coin_correlation(symbol, direction, timeframe='1h'):
    leaders = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'LINKUSDT']
    positive_votes = 0
    for coin in leaders:
        if coin == symbol:
            continue
        try:
            df1 = get_coin_data(symbol, timeframe)
            df2 = get_coin_data(coin, timeframe)
            if df1 is None or df2 is None:
                continue
            merged = pd.merge(df1, df2, on='timestamp', suffixes=('', '_peer'))
            if len(merged) < 10:
                continue
            corr = merged['close'].corr(merged['close_peer'])
            if (direction == 'bullish' and corr > 0.3) or (direction == 'bearish' and corr < -0.3):
                positive_votes += 1
        except:
            continue
    return positive_votes >= 3  # דרוש לפחות 3 אישורים ממטבעות מובילים

def evaluate_pattern_confidence(pattern_name):
    strong_patterns = ['Head and Shoulders', 'Double Top', 'Double Bottom', 'Bullish Flag', 'Bearish Flag', 'W Pattern', 'M Pattern']
    return pattern_name in strong_patterns

def ai_ensemble_decision(prob, volume, rsi, stability, btc_corr, pattern_conf, multi_corr=None):
    votes = [prob >= 70, volume, rsi, stability, btc_corr, pattern_conf]
    if multi_corr is not None:
        votes.append(multi_corr)
    return sum(votes) >= 5