#!/usr/bin/env python
import os
import sys

if "USE_NEWRELIC" in os.environ and "celeryd" in sys.argv:
    import newrelic.agent

    newrelic.agent.initialize()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "crate_project", "apps")))

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
