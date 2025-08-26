import os
from dotenv import load_dotenv

# Load environment variables from config.env
load_dotenv('config.env', override=True)

# Database Settings
DB_URI = os.environ.get("DATABASE_URL", os.environ.get("MONGO_URL", ""))
DB_NAME = os.environ.get("DATABASE_NAME", "cphdlust")

# Shortlink Settings (Token System)
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "ziplinker.net")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "4b884da539a2f5d579e2a6f805e623c7a082a3b1")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 43200)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "False").lower() == "true"
TUT_VID = os.environ.get("TUT_VID", "https://t.me/ultroid_official/18")

# Bot Settings
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
TELEGRAM_API = os.environ.get('TELEGRAM_API', '')
TELEGRAM_HASH = os.environ.get('TELEGRAM_HASH', '')
FSUB_ID = os.environ.get('FSUB_ID', '')
DUMP_CHAT_ID = os.environ.get('DUMP_CHAT_ID', '')
MONGO_URL = os.environ.get('MONGO_URL', '')
ADMINS = os.environ.get('ADMINS', '') 
