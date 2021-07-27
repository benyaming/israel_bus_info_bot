from os import getenv


TOKEN = getenv('TOKEN')

WEBAPP_HOST = getenv('WEBAPP_HOST')
WEBAPP_PORT = getenv('WEBAPP_PORT')
WEBHOOK_PATH = getenv('WEBHOOK_PATH')
WEBHOOK_URL = getenv('WEBHOOK_URL')

DOCKER_MODE = getenv('DOCKER_MODE')

DB_URL = getenv('DB_URL')
DB_NAME = getenv('DB_NAME')
DB_COLLECTION_NAME = getenv('DB_COLLECTION_NAME')

PERIOD = int(getenv('PERIOD', 5))  # how often message updates (seconds)
TTL = int(getenv('TTL', 900))  # how long message updates (seconds)

METRICS_DSN = getenv('METRICS_DSN')
METRICS_TABLE_NAME = getenv('METRICS_TABLE_NAME')

SENTRY_KEY = getenv('SENTRY_KEY')
API_URL = getenv('API_URL')
MAPBOX_TOKEN = getenv('MAPBOX_TOKEN')

THROTTLE_QUANTITY = getenv('THROTTLE_QUANTITY', 30)
THROTTLE_PERIOD = getenv('THROTTLE_PERIOD', 3)
