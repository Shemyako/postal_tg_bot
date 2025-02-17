from os import environ as env
from dotenv import load_dotenv


load_dotenv('.env')

DATABASE_URL = env.get("DATABASE_URL")
BOT_TOKEN = env.get("BOT_TOKEN")
DOMEN = env.get("DOMEN")

LOG_LEVEL = env.get('LOG_LEVEL') or 'INFO'

whitelist = set()
