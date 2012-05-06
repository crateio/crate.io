import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "apps")))

import newrelic.agent
newrelic.agent.initialize()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
