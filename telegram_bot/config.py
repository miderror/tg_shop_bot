import os
import sys
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

DJANGO_PROJECT_ROOT = Path(__file__).resolve().parent.parent / 'admin_panel'
sys.path.append(str(DJANGO_PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django

django.setup()

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBHOOK_URL = f'{BASE_WEBHOOK_URL}{WEBHOOK_PATH}'

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT"))

REQUIRED_CHAT_IDS = os.getenv("REQUIRED_CHAT_IDS").split(',')

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_RETURN_URL = os.getenv("YOOKASSA_RETURN_URL", "https://t.me/")

WEBHOOK_YOOKASSA_PATH = os.getenv("WEBHOOK_YOOKASSA_PATH", "/yookassa_payment_webhook")

USER_UPDATE_INTERVAL = timedelta(days=1)
ITEMS_PER_PAGE = 5
MAX_MESSAGE_TEXT_LENGTH = 4000
