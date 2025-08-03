import matplotlib.pyplot as plt
import pandas as pd
import os

def generate_trade_chart(df, symbol, direction, entry, sl, tp, filename="last_trade.png"):
    fig, ax = plt.subplots(figsize=(10, 5))
    df = df.tail(60).copy()
    df['index'] = range(len(df))

    # צבעים לנרות
    colors = ['green' if c >= o else 'red' for c, o in zip(df['close'], df['open'])]

    # ציור נרות
    for i in range(len(df)):
        ax.plot([df['index'][i], df['index'][i]], [df['low'][i], df['high'][i]], color='black', linewidth=0.8)
        ax.plot([df['index'][i], df['index'][i]], [df['open'][i], df['close'][i]], color=colors[i], linewidth=4)

    # קווי TP/SL/Entry
    ax.axhline(entry, color='blue', linestyle='--', label='כניסה')
    ax.axhline(sl, color='red', linestyle='--', label='סטופ')
    ax.axhline(tp, color='green', linestyle='--', label='טייק')

    # תחזית
    forecast_x = [df['index'].iloc[-1], df['index'].iloc[-1] + 5]
    forecast_y = [entry, tp if direction == 'bullish' else sl]
    ax.plot(forecast_x, forecast_y, color='purple', linestyle='dotted', linewidth=2, label='תחזית')

    ax.set_title(f"{symbol} - {direction.upper()} תרחיש")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    output_path = os.path.join(os.getcwd(), filename)
    plt.savefig(output_path)
    plt.close()
    return output_path