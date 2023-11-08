import os

# gunicorn.conf.py
bind = '0.0.0.0'.format(os.getenv('DJANGO_BACKEND_PORT', '8000'))
workers = int(os.getenv('GUNICORN_LOG_WORKERS', '3'))
# Access log - records incoming HTTP requests
accesslog = "/opt/immobyte/log/gunicorn/immobyte.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "/opt/immobyte/log/gunicorn/immobyte.error.log"
# How verbose the Gunicorn error logs should be
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
