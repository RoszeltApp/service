import os
from dotenv import load_dotenv


load_dotenv()

# App
APP_ENDPOINT = os.getenv('APP_ENDPOINT')
APP_TITLE = 'Web API'
APP_VERSION = os.getenv('APP_VERSION')
APP_DESCRIPTION = 'MVP Version'

# PostgresSQL
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USERNAME')
DB_PW = os.getenv('DB_PASSWORD')
DB_DB = os.getenv('DB_NAME')
DB_URI = f'postgresql://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_DB}'
DB_QUERY_ALLOWED_MAX_ARGS = 32767

# JWT
APP_JWT_SECRET = os.getenv('JWT_SECRET_KEY')
