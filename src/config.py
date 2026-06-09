import os

from dotenv import load_dotenv

load_dotenv()

YT_API_KEY = os.getenv('YT_API_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_LIFETIME_MINUTES = int(os.getenv('JWT_LIFETIME_MINUTES'))
DB_URL = os.getenv('DB_URL')
