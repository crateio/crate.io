#!/usr/bin/env python
import os
import sys

if "USE_NEWRELIC" in os.environ and "celeryd" in sys.argv:
    import newrelic.agent

    newrelic.agent.initialize()

try:
    import pinax
except ImportError:
    sys.stderr.write("Error: Can't import Pinax. Make sure you are in a "
        "virtual environment that has\nPinax installed.\n")
    sys.exit(1)
else:
    import pinax.env

from django.core.management import execute_from_command_line

pinax.env.setup_environ(__file__, relative_project_path=["crate_project"])

if __name__ == "__main__":
    execute_from_command_line()
