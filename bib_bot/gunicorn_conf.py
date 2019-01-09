import multiprocessing
from os import path
import settings

bind = '0.0.0.0:8443'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = path.join(settings.logs_path, 'gunicorn_access_log')
