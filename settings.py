from os import environ


TOKEN = environ.get('TOKEN')

WEBAPP_HOST = environ.get('WEBAPP_HOST')
WEBAPP_PORT = environ.get('WEBAPP_PORT')
WEBHOOK_PATH=environ.get('WEBHOOK_PATH')

IS_SERVER = environ.get('IS_SERVER')

DB_PARAMS = environ.get('DB_PARAMS')

R_HOST = environ.get('R_HOST')
R_PORT = environ.get('R_PORT')

RMQ_USER = environ.get('RMQ_USER')
RMQ_PASS = environ.get('RMQ_PASS')
RMQ_HOST = environ.get('RMQ_HOST')
RMQ_PORT = environ.get('RMQ_PORT')

PERIOD = environ.get('PERIOD')
TTL = environ.get('TTL')
