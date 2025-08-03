from pattern_bot.indicators import get_ohlcv, is_volume_strong, is_rsi_extreme

def get_star_rating(pattern_name, symbol_name=None, timeframe='15m', confirmed=True):
    """
    דירוג של תבנית לפי השם והאם אושרה על ידי מגמה.
    4 כוכבים = תבנית עם מגמה + אינדיקציה תומכת (volume או RSI).
    5 כוכבים = תבנית חזקה + אישור.
    6 כוכבים = תבנית חזקה מאוד + ווליום גבוה + מגמה ברורה.
    """
    rating = 1
    pattern_name = pattern_name.lower()

    if 'engulfing' in pattern_name:
        rating = 3
    if 'hammer' in pattern_name or 'shooting star' in pattern_name:
        rating = 4
    if 'doji' in pattern_name:
        rating = 2
    if 'w pattern' in pattern_name or 'm pattern' in pattern_name:
        rating = 5
    if 'strong' in pattern_name:
        rating = 6
    if 'morning star' in pattern_name:
        rating = 5
    if 'evening star' in pattern_name:
        rating = 5  

    # דירוג 4 – רק אם יש גם volume/RSI חזק
    if rating == 4 and symbol_name:
        df = get_ohlcv(symbol_name, timeframe)
        if is_volume_strong(df) or is_rsi_extreme(df):
            rating = 4
        else:
            rating = 3  # אין חיזוק – מורידים

    if confirmed:
        rating += 1

    return min(rating, 6)