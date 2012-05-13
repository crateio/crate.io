import os

if "USE_NEWRELIC" in os.environ:
    import newrelic.agent
    newrelic.agent.initialize()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
