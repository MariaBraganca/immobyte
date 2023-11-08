# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 3
# Access log - records incoming HTTP requests
accesslog = "/opt/immobyte/log/gunicorn/immobyte.access.log"
# Error log - records Gunicorn server goings-on
errorlog = "/opt/immobyte/log/gunicorn/immobyte.error.log"
# How verbose the Gunicorn error logs should be
loglevel = "debug"
