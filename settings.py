from os import environ


TOKEN = environ.get('TOKEN')

WEBAPP_HOST = environ.get('WEBAPP_HOST')
WEBAPP_PORT = environ.get('WEBAPP_PORT')
WEBHOOK_PATH = environ.get('WEBHOOK_PATH')

IS_SERVER = environ.get('IS_SERVER')

DB_HOST = environ.get('DB_HOST')
DB_PORT = environ.get('DB_PORT')
DB_USER = environ.get('DB_USER')
DB_PASS = environ.get('DB_PASS')
DB_NAME = environ.get('DB_NAME')
DB_PARAMS = f'dbname={DB_NAME} user={DB_USER} password={DB_PASS} ' \
            f'host={DB_HOST} port={DB_PORT}'

PERIOD = int(environ.get('PERIOD'))  # how often message updates (seconds)
TTL = 900  # how long message updates (seconds)
