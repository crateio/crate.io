web: gunicorn crateweb.wsgi:application -w 3 -k eventlet -c gunicorn.conf
worker: python manage.py celeryd -B --loglevel=info -c 2
