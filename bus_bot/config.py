from os import getenv


TOKEN = getenv('TOKEN')

WEBAPP_HOST = getenv('WEBAPP_HOST')
WEBAPP_PORT = getenv('WEBAPP_PORT')
WEBHOOK_PATH = getenv('WEBHOOK_PATH')
WEBHOOK_URL = getenv('WEBHOOK_URL')

DOCKER_MODE = getenv('DOCKER_MODE')

DB_HOST = getenv('DB_HOST')
DB_PORT = getenv('DB_PORT')
DB_USER = getenv('DB_USER')
DB_PASS = getenv('DB_PASS')
DB_NAME = getenv('DB_NAME')
DSN = f'dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}'

PERIOD = int(getenv('PERIOD', 5))  # how often message updates (seconds)
TTL = int(getenv('TTL', 900))  # how long message updates (seconds)

METRICS_DSN = getenv('METRICS_DSN')
METRICS_TABLE_NAME = getenv('METRICS_TABLE_NAME')

SENTRY_KEY = getenv('SENTRY_KEY')
API_URL = getenv('API_URL')
