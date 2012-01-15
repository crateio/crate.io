import pinax.env

from django.core.wsgi import get_wsgi_application

# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)

# set application for WSGI processing
application = get_wsgi_application()
