from os import environ


TOKEN = '709546621:AAEIZIVW9EOXCno21PPe8AZnHxNc5KX5LDU'

WEBAPP_HOST = environ.get('WEBAPP_HOST')
WEBAPP_PORT = environ.get('WEBAPP_PORT')

IS_SERVER = environ.get('IS_SERVER')

R_HOST = environ.get('R_HOST')
R_PORT = environ.get('R_PORT')

RMQ_USER = environ.get('RMQ_USER')
RMQ_PASS = environ.get('RMQ_PASS')
RMQ_HOST = environ.get('RMQ_HOST')
RMQ_PORT = environ.get('RMQ_PORT')

PERIOD = environ.get('PERIOD')
TTL = environ.get('TTL')
