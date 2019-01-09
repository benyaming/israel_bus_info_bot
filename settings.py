from os import environ


TOKEN = environ.get('TOKEN')

IS_SERVER = environ.get('IS_SERVER')
logs_path = environ.get('logs_path')

r_host = environ.get('r_host')
r_port = environ.get('r_port')

rmq_user = environ.get('rmq_user')
rmq_pass = environ.get('rmq_pass')
rmq_host = environ.get('rmq_host')
rmq_port = environ.get('rmq_port')

PERIOD = int(environ.get('period'))
TTL = int(environ.get('ttl'))
