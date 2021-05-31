from os import environ


TOKEN = environ.get('TOKEN')

WEBAPP_HOST = environ.get('WEBAPP_HOST')
WEBAPP_PORT = environ.get('WEBAPP_PORT')
WEBHOOK_PATH = environ.get('WEBHOOK_PATH')
WEBHOOK_URL = environ.get('WEBHOOK_URL')

DOCKER_MODE = environ.get('DOCKER_MODE')

DB_HOST = environ.get('DB_HOST')
DB_PORT = environ.get('DB_PORT')
DB_USER = environ.get('DB_USER')
DB_PASS = environ.get('DB_PASS')
DB_NAME = environ.get('DB_NAME')
DSN = f'dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}'

PERIOD = int(environ.get('PERIOD', 5))  # how often message updates (seconds)
TTL = int(environ.get('TTL', 900))  # how long message updates (seconds)

METRICS_DSN = environ.get('METRICS_DSN')
METRICS_TABLE_NAME = environ.get('METRICS_TABLE_NAME')
