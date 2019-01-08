from os import environ


TOKEN = environ.get('TOKEN')
BOT_HOST = environ.get('BOT_HOST')
BOT_PORT = environ.get('BOT_PORT')
URI = environ.get('URI')

IS_SERVER = environ.get('IS_SERVER')
logs_path = environ.get('logs_path')

r_host = environ.get('r_host')
r_port = environ.get('r_port')

PERIOD = environ.get('period')
TTL = environ.get('ttl')
