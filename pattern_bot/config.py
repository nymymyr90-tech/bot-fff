import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

OPEN_TRADES_CSV = os.path.join(BASE_DIR, 'open_trades.csv')
SIGNALS_LOG_FILE = os.path.join(BASE_DIR, 'signals_log.csv')
PENDING_SIGNALS_FILE = os.path.join(BASE_DIR, 'pending_signals.csv')

TELEGRAM_BOT_TOKEN = "8171727589:AAGf_CcSmvFZaELhaX_2NCMnSa4RYUb9pR0"
TELEGRAM_CHAT_ID_GROUP = -4834845574   # ID של הקבוצה
TELEGRAM_CHAT_ID_USER = 1383530308     # ID של היוזר שלך